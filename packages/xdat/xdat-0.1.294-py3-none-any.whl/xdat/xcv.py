import numpy as np
import pandas as pd
from scriptine import path
import cv2
from PIL import Image, PngImagePlugin, JpegImagePlugin
from tqdm import tqdm
import matplotlib.pyplot as plt
from . import xplots, xstats


def angle_difference(a1, a2):
    return 180 - np.abs(np.abs(a1 - a2) - 180)


def kp_angle_dist(kp1, kp2):
    return angle_difference(kp1.angle, kp2.angle)


def kp_euclidean_distance(kp1, kp2):
    """Compute pairwise Euclidean distances between two keypoints."""

    dx = kp1.pt[0] - kp2.pt[0]
    dy = kp1.pt[1] - kp2.pt[1]
    distance = np.sqrt(dx**2 + dy**2)
    return distance


def kp_relative_distances(keypoint, keypoints, kp_dist_func=kp_euclidean_distance):
    """Compute distances from the given keypoint to all other keypoints."""

    return [kp_dist_func(keypoint, kp) for kp in keypoints]


def match_spatial_consistency(match, matches, query_keypoints, train_keypoints):
    return match_consistency(match, matches, query_keypoints, train_keypoints, kp_dist_func=kp_euclidean_distance)


def match_angle_consistency(match, matches, query_keypoints, train_keypoints):
    return match_consistency(match, matches, query_keypoints, train_keypoints, kp_dist_func=kp_angle_dist)


def match_consistency(match, matches, query_keypoints, train_keypoints, kp_dist_func=kp_euclidean_distance):
    # Extract keypoints for the current match
    query_kp = query_keypoints[match.queryIdx]
    train_kp = train_keypoints[match.trainIdx]

    # Extract keypoints for all matches
    matched_query_kps = [query_keypoints[m.queryIdx] for m in matches]
    matched_train_kps = [train_keypoints[m.trainIdx] for m in matches]

    # Compute relative distances in both query and train images
    query_distances = kp_relative_distances(query_kp, matched_query_kps, kp_dist_func=kp_dist_func)
    train_distances = kp_relative_distances(train_kp, matched_train_kps, kp_dist_func=kp_dist_func)

    # Compute difference between the sets of distances
    difference = np.abs(np.array(query_distances) - np.array(train_distances))

    # Return the mean difference (or any other metric of your choice)
    return np.mean(difference)


def match_analysis(matches, kp1, kp2):
    """ Given kp matches, return a df with added analysis """

    rows = []

    for match in matches:
        kp_a = kp1[match.queryIdx]
        kp_b = kp2[match.trainIdx]

        angle_diff = angle_difference(kp_a.angle, kp_b.angle)
        spatial_consist = match_spatial_consistency(match, matches, kp1, kp2)
        angle_consist = match_angle_consistency(match, matches, kp1, kp2)

        row = {
            'kp_dist': match.distance,
            'angle_diff': angle_diff,
            'spatial_consistency': spatial_consist,
            'angle_consistency': angle_consist
        }

        rows.append(row)

    df_matches = pd.DataFrame(rows)
    return df_matches


def match_score(df_matches, plot=False):
    """ Given a match analysis df (see match_analysis)m returns a match score """

    df = df_matches.sort_values('kp_dist')
    df['score'] = df.kp_dist * df.spatial_consistency * df.angle_consistency * 0.000001

    if plot:
        xplots.plot_multi(df, kind='hist', y='kp_dist', hist_range=[0, 100])
        xplots.plot_multi(df, kind='kde', y='score', xlim=[0, 1])
        xplots.plot_multi(df, kind='line', x='kp_dist', y='angle_diff')
        xplots.plot_multi(df, kind='line', x='kp_dist', y='spatial_consistency')
        xplots.plot_multi(df, kind='line', x='kp_dist', y='angle_consistency')
        xplots.plot_multi(df, kind='line', x='kp_dist', y='score')

    # identical image
    if df.score.sum() == 0:
        return 0

    score, score_density = xstats.x_kde_mode(df.score.to_numpy())

    return score


def process_video(video_in_path, video_out_path=None, frames_folder=None, plot_idx=None, max_idx=None, quality=90, pfunc=None, every=1, out_every=1, get_frame_idx=None):
    """
    :param video_in_path: path to input video
    :param video_out_path: path to output video
    :param frames_folder: path to output frames
    :param plot_idx: which idx to plot
    :param max_idx: when to stop processing
    :param quality: quality of output video (video_out_path)
    :param pfunc: pfunc(img, frame=0), img in RGB format, returns updated image also in RGB format
    :param every: process every k frames
    :param out_every: output to video every k frames (can be less than 'every'), repeats last processed multiple times
    :param get_frame_idx: if used, returns an image of that frame only
    """

    video_in_path = path(video_in_path)
    vidcap = cv2.VideoCapture(video_in_path)

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    print('frame size=', frame_size)

    if frames_folder:
        frames_folder = path(frames_folder)
        frames_folder.ensure_dir()

    out = None
    if video_out_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_out_path, fourcc, fps, frame_size)
        out.set(cv2.VIDEOWRITER_PROP_QUALITY, quality)

    last_image = None
    for idx in tqdm(range(frame_count)):
        success, image = vidcap.read()      # image is BGR

        if not success:
            print(f'{idx}) error reading image')
            break

        if get_frame_idx is not None:
            if idx < get_frame_idx:
                continue
            else:
                return image[:, :, ::-1]   # make RGB

        should_process = idx % every == 0
        if not should_process and not out:
            continue

        image = image[:, :, ::-1]       # Image is now RGB

        if should_process and pfunc:
            last_image = image = pfunc(image, frame=idx)  # requires RGB

        if last_image is not None and out and idx % out_every == 0:
            out.write(last_image[:, :, ::-1])  # requires BGR

        if frames_folder:
            frame_name = f"{video_in_path.namebase}__frame{idx:05d}.jpg"
            # frame_path = frames_folder.joinpath(video_in_path.namebase)
            # frame_path.ensure_dir()
            frame_path = frames_folder.joinpath(frame_name)
            cv2.imwrite(frame_path, image[:, :, ::-1])  # requires BGR

        if plot_idx == idx:
            image2 = image
            plt.imshow(image2)   # requires RGB
            plt.axis('off')
            plt.tight_layout()
            plt.show()

        if max_idx is not None and idx >= max_idx:
            break

    if out:
        out.release()


def calc_xyxy_overlap(rect1, rect2):
    # Unpack the coordinates for readability
    x1_rect1, y1_rect1, x2_rect1, y2_rect1 = rect1
    x1_rect2, y1_rect2, x2_rect2, y2_rect2 = rect2

    # Find the dimensions of the intersection rectangle
    x_overlap = max(0, min(x2_rect1, x2_rect2) - max(x1_rect1, x1_rect2))
    y_overlap = max(0, min(y2_rect1, y2_rect2) - max(y1_rect1, y1_rect2))

    # Calculate the area of intersection rectangle
    intersection_area = x_overlap * y_overlap

    # Calculate the area of both rectangles
    area_rect1 = (x2_rect1 - x1_rect1) * (y2_rect1 - y1_rect1)
    area_rect2 = (x2_rect2 - x1_rect2) * (y2_rect2 - y1_rect2)

    # Calculate the total area covered by the two rectangles
    total_area = area_rect1 + area_rect2 - intersection_area

    # Check for any overlap
    if intersection_area == 0:
        return 0, 0, 0  # There is no overlap

    overlap_percent_rect1 = (intersection_area / area_rect1)
    overlap_percent_rect2 = (intersection_area / area_rect2)
    overlap_perc_union = intersection_area / total_area

    return overlap_percent_rect1, overlap_percent_rect2, overlap_perc_union


def calc_xyxy_center_dist(rect1, rect2):
    # Unpack the coordinates for readability
    x1_rect1, y1_rect1, x2_rect1, y2_rect1 = rect1
    x1_rect2, y1_rect2, x2_rect2, y2_rect2 = rect2

    center1_x = (x1_rect1+x2_rect1)/2
    center1_y = (y1_rect1 + y2_rect1) / 2
    center2_x = (x1_rect2+x2_rect2)/2
    center2_y = (y1_rect2 + y2_rect2) / 2

    dist = np.sqrt(np.square(center1_x-center2_x) + np.square(center1_y - center2_y))
    return dist


def crop_zoom_center(img, factor=2):
    """
    Given an image, "zoom in" by cropping
    """
    width, height = img.size

    crop_width, crop_height = int(width/factor), int(height/factor)

    left = int((width - crop_width) / 2)
    upper = int((height - crop_height) / 2)
    right = left + crop_width
    lower = upper + crop_height

    cropped_image = img.crop((left, upper, right, lower))
    return cropped_image


def resize_and_center_crop(original_image, target_size=None, portrait_width=None):
    """
    Resize an image to a target size, maintaining aspect ratio and cropping as needed from the center.

    :param img_path: Path to the image file
    :param target_size: A tuple (width, height) for the target size
    :param portrait_width: given a size (width), first rotates image to portrait mode, then resizes (keeping aspect ratio)
    :return: A resized and cropped PIL Image object
    """
    assert sum([bool(target_size), bool(portrait_width)]) == 1, 'must specify one and only one'

    as_np = False
    if isinstance(original_image, np.ndarray):
        as_np = True
        original_image = Image.fromarray(original_image)

    original_width, original_height = original_image.size

    if portrait_width:
        if original_width > original_height:
            original_image = original_image.rotate(90, expand=True)
            original_width, original_height = original_image.size

        target_width = portrait_width
        target_height = int(target_width * original_height / original_width)

    else:  # target_size
        target_width, target_height = target_size

    if (original_width > original_height) != (target_width > target_height):
        original_image = original_image.rotate(90, expand=True)
        original_width, original_height = original_image.size

    # Calculate the aspect ratio of the target and original image
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height

    # Resize the image while maintaining aspect ratio
    if original_ratio < target_ratio:  # Original is taller
        new_width = target_width
        new_height = max(target_height, int(round(new_width / original_ratio)))
    else:  # Original is wider
        new_height = target_height
        new_width = max(target_width, int(round(new_height * original_ratio)))

    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate coordinates for cropping
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    # Crop the center of the image
    cropped_image = resized_image.crop((left, top, right, bottom))

    if as_np:
        cropped_image = np.array(cropped_image)

    return cropped_image


def x_save_image_with_correct_extension(image: Image.Image, output_path: str):
    """
    Saves a PIL Image with the correct extension based on its class type.

    - Uses PNG if the image is a PngImageFile.
    - Uses JPEG if the image is a JpegImageFile.
    - Falls back to PNG if unsure.
    """
    # Determine format based on class type
    if isinstance(image, PngImagePlugin.PngImageFile):
        format = "PNG"
    elif isinstance(image, JpegImagePlugin.JpegImageFile):
        format = "JPEG"
    else:
        # Fallback: Check if transparency exists
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            format = "PNG"
        else:
            format = "JPEG"

    extension = '.jpg' if format == 'JPEG' else '.png'
    final_path = f"{output_path}{extension}"

    image.save(final_path, format=format)
    return final_path