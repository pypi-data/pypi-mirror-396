#!/usr/bin/env python3
"""
credit: https://pypi.org/project/xdat/
(diagnose-gpu.py)
Quick GPU/TensorFlow diagnostics for Ubuntu EC2 boxes.

What it checks:
  - OS, kernel, Python, virtualenv
  - nvidia-smi / driver branch
  - Kernel vs userspace NVIDIA driver versions (mismatch detection)
  - Kernel module load + DKMS status, Secure Boot state
  - PCI device presence (lspci)
  - Key NVIDIA runtime libs resolvable by the dynamic linker
  - Presence & permissions of /dev/nvidia* device nodes
  - Env vars that commonly break visibility (CUDA_VISIBLE_DEVICES, LD_LIBRARY_PATH)
  - CUDA toolkit presence (nvcc), container detection
  - TensorFlow import, version, build info (CUDA/cuDNN), visible GPUs
  - Optional tiny GPU matmul to prove compute

Usage:
  python diagnose-gpu.py
  python diagnose-gpu.py --no-matmul       # skip compute test
  python diagnose-gpu.py --verbose         # extra details
"""

import argparse
import ctypes
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path

def run(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.strip()
    except FileNotFoundError:
        return 127, f"{cmd[0]}: not found"

def section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def check_system(verbose=False):
    section("System")
    try:
        with open("/etc/os-release") as f:
            osr = f.read().strip()
    except Exception:
        osr = "(could not read /etc/os-release)"
    print(f"OS release:\n{osr}\n")
    print(f"Kernel: {platform.release()}")
    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    in_venv = (hasattr(sys, "real_prefix") or sys.prefix != getattr(sys, "base_prefix", sys.prefix))
    print(f"Virtualenv: {'yes' if in_venv else 'no'} (prefix={sys.prefix})")
    if verbose:
        rc, pipv = run([sys.executable, "-m", "pip", "--version"])
        print(f"Pip: {pipv if rc==0 else '(pip not found)'}")
    # Container detection
    if Path("/.dockerenv").exists() or os.environ.get("container", "") or Path("/run/.containerenv").exists():
        print("Container: yes (running inside a container)")
    else:
        print("Container: no")

def parse_driver_version_from_proc():
    """
    /proc/driver/nvidia/version contains lines like:
    NVRM version: NVIDIA UNIX x86_64 Kernel Module  535.247.01  ...
    """
    p = Path("/proc/driver/nvidia/version")
    if not p.exists():
        return None
    try:
        txt = p.read_text()
        m = re.search(r"Kernel Module\s+([0-9]{3}\.[0-9]+)", txt)
        if not m:
            m = re.search(r"NVRM version:.*?\s([0-9]{3}\.[0-9]+)", txt)
        return m.group(1) if m else None
    except Exception:
        return None

def parse_nvml_or_userspace_version(nvsmi_output):
    """
    When nvidia-smi fails with NVML mismatch it often prints:
      'NVML library version: 535.274'
    Otherwise, when it works, it prints a table with a 'Driver Version' line.
    """
    # Try NVML library version first (failure mode)
    m = re.search(r"NVML library version:\s*([0-9]{3}\.[0-9]+)", nvsmi_output)
    if m:
        return m.group(1)
    # Try the normal working header
    m = re.search(r"Driver Version:\s*([0-9]{3}\.[0-9]+)", nvsmi_output)
    if m:
        return m.group(1)
    return None

def check_nvidia_smi():
    section("NVIDIA Driver (nvidia-smi)")
    rc, out = run(["nvidia-smi"])
    if rc == 0:
        print(out)
    else:
        print(out or "nvidia-smi failed")
        print("HINT: Install/enable the NVIDIA driver (e.g., `sudo ubuntu-drivers autoinstall` then reboot).")
    return rc, out

def check_kernel_vs_userspace_versions(nvsmi_rc, nvsmi_out):
    section("Driver versions: kernel module vs. userspace (NVML/libcuda)")
    kernel_ver = parse_driver_version_from_proc()
    userspace_ver = parse_nvml_or_userspace_version(nvsmi_out or "")

    print(f"Kernel module version: {kernel_ver or '(unavailable)'}")
    print(f"Userspace (NVML/libcuda) version: {userspace_ver or '(unavailable)'}")

    if kernel_ver and userspace_ver and kernel_ver != userspace_ver:
        print("DIAGNOSIS: ❌ Driver/library version mismatch — CUDA cannot initialize in this state.")
        print("FIX (one of):")
        print("  • `sudo ubuntu-drivers autoinstall && sudo update-initramfs -u && sudo reboot`")
        print("  • Or purge & reinstall a single branch, e.g.:")
        print("      sudo apt-get purge 'nvidia-*'")
        print("      sudo apt-get install nvidia-driver-535   # or 550/560, but be consistent")
    elif kernel_ver and userspace_ver and kernel_ver == userspace_ver:
        print("DIAGNOSIS: ✅ Kernel and userspace driver versions are consistent.")
    else:
        print("Note: could not retrieve both versions; see other sections for hints.")

def check_module_and_secure_boot(verbose=False):
    section("Kernel modules & Secure Boot")
    rc, out = run(["lsmod"])
    if rc == 0:
        loaded = "\n".join([ln for ln in out.splitlines() if ln.startswith("nvidia")])
        print(loaded if loaded else "(no nvidia* modules loaded)")
    else:
        print("(could not run lsmod)")

    # modinfo (module present on disk?)
    rc, out = run(["modinfo", "-F", "version", "nvidia"])
    if rc == 0:
        print(f"modinfo nvidia version: {out}")
    else:
        print("modinfo nvidia: not found (module not installed or not in kernel tree)")

    # DKMS status (helpful if using dkms-managed drivers)
    rc, out = run(["dkms", "status"])
    if rc == 0:
        lines = [ln for ln in out.splitlines() if "nvidia" in ln.lower()]
        print("DKMS:", "\n".join(lines) if lines else "(no nvidia dkms entries)")
    else:
        print("DKMS: (dkms not installed)")

    # Secure Boot state
    rc, out = run(["mokutil", "--sb-state"])
    if rc == 0:
        print(f"Secure Boot: {out}")
        if "enabled" in out.lower():
            print("HINT: With Secure Boot enabled, unsigned NVIDIA modules may not load.")
            print("      Either enroll MOK & sign modules or disable Secure Boot in firmware.")
    else:
        print("Secure Boot: (mokutil not available or not in EFI mode)")

    # Recent dmesg for NVIDIA errors (verbose only)
    if verbose:
        rc, out = run(["dmesg", "--ctime", "--color=never"])
        if rc == 0:
            errs = [ln for ln in out.splitlines() if "NVRM:" in ln or "nvidia" in ln.lower()]
            print("\nRecent NVIDIA-related dmesg lines (last ~50 shown):")
            print("\n".join(errs[-50:]) if errs else "(no NVIDIA-related dmesg lines found)")
        else:
            print("(could not read dmesg)")

def check_pci_devices():
    section("PCI devices (lspci)")
    rc, out = run(["lspci", "-nnk"])
    if rc == 0:
        gpus = [ln for ln in out.splitlines() if ("NVIDIA" in ln or "3D controller" in ln or "VGA compatible controller" in ln)]
        print("\n".join(gpus) if gpus else "(no NVIDIA adapters listed by lspci)")
    else:
        print("lspci not available (install pciutils).")

def check_key_libs(verbose=False):
    section("Dynamic Linker: CUDA/NVIDIA runtime libraries")
    libs = ["libcuda.so.1", "libnvidia-ml.so.1", "libnvidia-ptxjitcompiler.so.1"]
    all_ok = True
    for lib in libs:
        try:
            ctypes.CDLL(lib)
            print(f"OK: {lib} is loadable")
        except OSError as e:
            all_ok = False
            print(f"FAIL: {lib} not loadable -> {e}")
    print("\nldconfig cache (filtered):")
    rc, out = run(["ldconfig", "-p"])
    if rc == 0:
        lines = [ln for ln in out.splitlines() if any(s in ln for s in libs)]
        print("\n".join(lines) if lines else "(no matching entries)")
    else:
        print("(could not run ldconfig -p)")

    paths = [
        "/usr/lib/x86_64-linux-gnu",
        "/usr/lib/x86_64-linux-gnu/nvidia/current",
        "/lib/x86_64-linux-gnu",
    ]
    if verbose:
        print("\nFile presence check:")
        for base in paths:
            if os.path.isdir(base):
                for name in ("libcuda.so", "libcuda.so.1", "libnvidia-ml.so.1", "libnvidia-ptxjitcompiler.so.1"):
                    p = os.path.join(base, name)
                    if os.path.exists(p):
                        print("  exists:", p)

    if not all_ok:
        print(textwrap.dedent("""
        HINTS:
          • Install the matching runtime libraries for your driver branch, e.g.:
              sudo apt-get update
              sudo apt-get -y install libnvidia-compute-560 libnvidia-encode-560 libnvidia-decode-560 libnvidia-ptxjitcompiler-560
              sudo ldconfig
          • If libraries live under .../nvidia/current, add it to the linker config:
              echo "/usr/lib/x86_64-linux-gnu/nvidia/current" | sudo tee /etc/ld.so.conf.d/nvidia.conf
              sudo ldconfig
          • Re-open a new shell before re-testing.
        """).strip())

def check_device_nodes():
    section("Device nodes")
    devs = [f for f in os.listdir("/dev") if f.startswith("nvidia")]
    if devs:
        rc, out = run(["/bin/ls", "-l"] + [os.path.join("/dev", f) for f in devs])
        print(out)
        # Quick permission sanity (must be accessible by your user or group)
        for f in devs:
            p = Path("/dev") / f
            st = p.stat()
            # world-writable here is common on some distros; otherwise group is usually 'video'
            # We simply display group for awareness.
            try:
                import grp
                gname = grp.getgrgid(st.st_gid).gr_name
            except Exception:
                gname = str(st.st_gid)
            print(f"Note: {p} group={gname}")
        # nvidia-modprobe presence (helps auto-create device nodes)
        rc, _ = run(["which", "nvidia-modprobe"])
        if rc != 0:
            print("HINT: Install nvidia-modprobe to manage /dev nodes:")
            print("      sudo apt-get install nvidia-modprobe")
    else:
        print("No /dev/nvidia* nodes found.")
        print("HINT: Try loading modules & creating nodes:\n"
              "  sudo modprobe nvidia_uvm && sudo /usr/bin/nvidia-modprobe -u -c=0")

def check_env():
    section("Environment variables that affect visibility")
    keys = ["CUDA_VISIBLE_DEVICES", "LD_LIBRARY_PATH", "TF_ENABLE_ONEDNN_OPTS"]
    for key in keys:
        if key in os.environ:
            val = os.environ[key]
            print(f"{key} = {val!r}")
        else:
            print(f"{key} is NOT set")

    # Detailed CUDA_VISIBLE_DEVICES interpretation
    val = os.environ.get("CUDA_VISIBLE_DEVICES", None)
    if val is None:
        print("INFO: CUDA_VISIBLE_DEVICES is not set (all GPUs visible).")
    elif val in ("", "None"):
        print("HINT: CUDA_VISIBLE_DEVICES hides all GPUs. Run: unset CUDA_VISIBLE_DEVICES")
    else:
        print(f"INFO: CUDA_VISIBLE_DEVICES is set to {val!r} — only those GPUs are visible.")

    # Mild nudge about LD_LIBRARY_PATH issues (leading or trailing colons)
    ld = os.environ.get("LD_LIBRARY_PATH")
    if ld is not None and (ld.startswith(":") or ld.endswith(":")):
        print("Note: LD_LIBRARY_PATH has an empty entry (starts/ends with ':'); usually harmless but can be cleaned up.")

def check_cuda_toolkit(verbose=False):
    section("CUDA toolkit (optional)")
    rc, out = run(["nvcc", "--version"])
    if rc == 0:
        print(out)
    else:
        print("nvcc not found (CUDA toolkit not installed in PATH). This is fine for TF wheels.")
    if verbose:
        # Show where libcuda/libnvml resolve from at runtime
        for lib in ("libcuda.so.1", "libnvidia-ml.so.1"):
            rc, out = run(["bash", "-lc", f"ldd $(python - <<'PY'\nimport ctypes,sys\nimport os\ntry:\n    print(ctypes.util.find_library('{lib[:-3]}') or '')\nexcept Exception:\n    print('')\nPY\n) 2>/dev/null"])
            # This ldd trick is best-effort; often too noisy. Keep quiet by default.

def check_tensorflow(no_matmul=False, verbose=False):
    section("TensorFlow")
    try:
        import tensorflow as tf
    except Exception as e:
        print("FAIL: Could not import TensorFlow:", e)
        print("HINT: Activate the correct venv and install TF, e.g.:")
        print("  source ~/venv/bin/activate && pip install 'tensorflow==2.13.1'")
        return

    # Eagerly force CUDA init to surface cuInit errors early
    try:
        _ = tf.config.get_visible_devices()
    except Exception:
        pass

    print("TF version:", tf.__version__)
    try:
        build = {}
        try:
            if hasattr(tf.sysconfig, "get_build_info"):
                build = tf.sysconfig.get_build_info()
        except Exception:
            pass
        if not build:
            try:
                from tensorflow.python.platform import build_info as bi
                build = getattr(bi, "build_info", {})
            except Exception:
                build = {}
        if build:
            print("Build info:", {k: build.get(k) for k in ("is_cuda_build","cuda_version","cudnn_version")})
        else:
            print("Build info: <unavailable>")
    except Exception as e:
        print("Note: could not retrieve TF build info:", e)

    try:
        # Also prints driver/DSO mismatch messages if present
        gpus = tf.config.list_physical_devices("GPU")
        print("Visible GPUs:", gpus)
    except Exception as e:
        print("FAIL: tf.config.list_physical_devices('GPU') raised:", e)
        gpus = []

    if gpus and not no_matmul:
        print("\nRunning tiny GPU matmul to confirm compute…")
        try:
            t0 = time.time()
            with tf.device("/GPU:0"):
                a = tf.random.normal([2048, 2048])
                b = tf.random.normal([2048, 2048])
                _ = (a @ b).numpy()
            dt = time.time() - t0
            print(f"Matmul ✅ (GPU) in {dt:.3f}s")
        except Exception as e:
            print("Matmul test failed:", e)
            print("HINT: If this errors with CUDA/ptxjit, ensure libnvidia-ptxjitcompiler.so.1 is resolvable.")
    elif not gpus:
        print(textwrap.dedent("""
        HINTS:
          • If nvidia-smi works but GPUs=[]: usually a missing runtime lib (libcuda/libnvidia-ml/libnvidia-ptxjitcompiler).
          • Ensure driver kernel module and userspace NVML/libcuda versions MATCH (see 'Driver versions' section).
          • Make sure you're in the same venv where TF is installed.
          • Verify CUDA_VISIBLE_DEVICES is not hiding devices.
        """).strip())

def main():
    ap = argparse.ArgumentParser(description="Diagnose TensorFlow GPU visibility on Ubuntu.")
    ap.add_argument("--no-matmul", action="store_true", help="Skip the GPU matmul test.")
    ap.add_argument("--verbose", action="store_true", help="Print extra details.")
    args = ap.parse_args()

    print("diagnose-gpu.py — GPU & TensorFlow quick health check")
    check_system(verbose=args.verbose)
    nvsmi_rc, nvsmi_out = check_nvidia_smi()
    check_kernel_vs_userspace_versions(nvsmi_rc, nvsmi_out)
    check_module_and_secure_boot(verbose=args.verbose)
    check_pci_devices()
    check_key_libs(verbose=args.verbose)
    check_device_nodes()
    check_env()
    check_cuda_toolkit(verbose=args.verbose)
    check_tensorflow(no_matmul=args.no_matmul, verbose=args.verbose)

    print("\nDone. If something failed, scroll up to the HINTS near the failure.")

if __name__ == "__main__":
    main()
