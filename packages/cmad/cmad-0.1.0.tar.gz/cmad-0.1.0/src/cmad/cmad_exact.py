# cmad_exact.py

import glob
import os
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================
# 0. Core helper functions
# ============================

def rgb_to_gray_image_conversion(filelist, device="cpu"):
    """
    Read PNGs, convert to grayscale.
    Returns:
      gray_image_list: list of 2D tensors [H,W] on device
      rgb_image_list: list of 3D tensors [H,W,3] on device
    """
    gray_image_list = []
    rgb_image_list = []

    for file in filelist:
        image_rgb = cv2.imread(file)  # BGR, uint8
        if image_rgb is None:
            print(f"Warning: could not read {file}")
            continue

        gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

        gray_image_tensor = torch.tensor(gray_image, dtype=torch.float32, device=device)
        rgb_image_tensor = torch.tensor(image_rgb, dtype=torch.float32, device=device)

        gray_image_list.append(gray_image_tensor)
        rgb_image_list.append(rgb_image_tensor)

    return gray_image_list, rgb_image_list


def file_to_gray(gray_image_list, index_no, device="cpu"):
    """
    Return padded gray image (H+2, W+2) as tensor on device
    """
    gray_image = gray_image_list[index_no].to(device)
    padded_gray_image = F.pad(gray_image, (1, 1, 1, 1), "constant", 0)
    return padded_gray_image


# =========================================================
# Index utilities (for back-projection) - dynamic size
# =========================================================

def getIndices(x, kernel_size_h, kernel_size_w, stride_h, stride_w):
    indices = {}
    H = x.size(0)
    W = x.size(1)

    h_out = (H - kernel_size_h) // stride_h + 1
    w_out = (W - kernel_size_w) // stride_w + 1

    for i in range(h_out):
        for j in range(w_out):
            start_i = i * stride_h
            start_j = j * stride_w
            end_i = start_i + kernel_size_h
            end_j = start_j + kernel_size_w

            indices[(i, j)] = [
                (start_i, start_j),        # top-left
                (start_i, end_j - 1),      # top-right
                (end_i - 1, start_j),      # bottom-left
                (end_i - 1, end_j - 1),    # bottom-right
            ]
    return indices


def getIndices_in_orginal_gray(row, col, combined_indices):
    """
    Return list of (row,col) indices in padded original grid
    for a given pooled cell (row,col)
    """
    indices_list_gray_image = [
        index for sublist in combined_indices[(row, col)].values() for index in sublist
    ]
    return indices_list_gray_image


def build_combined_indices_dynamic(H, W,
                                   kernel_size_h=2, kernel_size_w=2,
                                   stride_h=2, stride_w=2):
    """
    Build mapping between:
    - padded original gray (H+2, W+2)
    - second-level pooled grid via 2x2 avg pool, stride 2
    Works for ANY H,W.

    This matches your original build_combined_indices_dynamic.
    """
    x = torch.arange(0, H * W, dtype=torch.float32).reshape(H, W)
    padded_x = F.pad(x, (1, 1, 1, 1), "constant", 0)

    y = F.avg_pool2d(
        padded_x.unsqueeze(0).unsqueeze(0),
        kernel_size=(kernel_size_h, kernel_size_w),
        stride=(stride_h, stride_w),
    ).squeeze()

    indices1 = getIndices(padded_x, kernel_size_h, kernel_size_w, stride_h, stride_w)
    indices2 = getIndices(y, kernel_size_h, kernel_size_w, stride_h, stride_w)

    combined_indices = {}
    for key2, value2 in indices2.items():
        temp_dict = {}
        for idx in value2:
            temp_dict[idx] = indices1[idx]
        combined_indices[key2] = temp_dict

    return combined_indices


# =========================================================
# Simple kernel (2x2) + diff construction
# =========================================================

def getKernel(input_tensor_ignored, device="cpu"):
    """
    Your original code returns a 2x2 ones kernel.
    """
    k = torch.ones((2, 2), dtype=torch.float32, device=device)
    return k


def get_diff_gray_image_kernel_list(gray_image_list, device="cpu"):
    """
    Compute difference images and associated kernels.
    Returns:
        diff_gray_image_list: list of [H,W] tensors
        diff_gray_image_kernel_list_2_2: list of [2,2] kernels
    """
    diff_gray_image_list = []
    diff_gray_image_kernel_list_2_2 = []

    for i in range(len(gray_image_list) - 1):
        img2 = gray_image_list[i + 1].to(device)
        img1 = gray_image_list[i].to(device)

        arr = (img2 - img1).clone().detach()  # [H,W]
        diff_gray_image_list.append(arr)

        kernel_arr = getKernel(arr, device=device)
        diff_gray_image_kernel_list_2_2.append(kernel_arr)

    return diff_gray_image_list, diff_gray_image_kernel_list_2_2


def get_diff_list_from_array(X, device="cpu"):
    """
    X: tensor [T,H,W] on device
    Build diff_gray_image_list and kernels like original code,
    but using generic array instead of images.
    """
    gray_image_list = [X[t] for t in range(X.shape[0])]
    return get_diff_gray_image_kernel_list(gray_image_list, device=device)


# =========================================================
# Sharpening / Conv (2x2 kernel, stride 2, pad 1)
# =========================================================

def apply_2x2_sharpening(input_tensor, kernel, device="cpu"):
    """
    input_tensor: [H,W] (torch)
    kernel: [2,2] (torch)
    Returns: numpy array [Hc, Wc] after conv2d
    """
    input_tensor = input_tensor.unsqueeze(0).unsqueeze(0).float().to(device)
    kernel_tensor = kernel.unsqueeze(0).unsqueeze(0).float().to(device)

    kH = kernel_tensor.size(2)
    kW = kernel_tensor.size(3)

    conv_layer = nn.Conv2d(
        in_channels=1,
        out_channels=1,
        kernel_size=(kH, kW),
        stride=(2, 2),
        padding=1,
        bias=False,
    ).to(device)

    with torch.no_grad():
        conv_layer.weight.data = kernel_tensor

    output = conv_layer(input_tensor)
    return output[0, 0].detach().cpu().numpy()


def get_kernel_applied_result_in_diff_gray_image(
    diff_gray_image_list,
    diff_gray_image_kernel_list_2_2,
    device="cpu"
):
    """
    For each diff image, apply 2x2 conv kernel (stride2, pad1).
    Returns list of 2D numpy arrays.
    """
    kernel_applied_result_in_diff_gray_image = []

    for i in range(len(diff_gray_image_list)):
        matrix = diff_gray_image_list[i]
        kernel = diff_gray_image_kernel_list_2_2[i]

        result = apply_2x2_sharpening(matrix, kernel, device=device)
        kernel_applied_result_in_diff_gray_image.append(result)

    return kernel_applied_result_in_diff_gray_image


# =========================================================
# Truncation: build [T, row, col, 4] from conv outputs
# =========================================================

def truncating_array_dynamic(original_array, device="cpu"):
    """
    original_array: list or array of shape [T,Hc,Wc]
    Output: [T, row, col, 4] with flattened 2x2 neighborhoods.
    row, col are computed from Hc,Wc, no hardcoding.
    """
    original_tensor = torch.tensor(original_array, dtype=torch.float32, device=device)

    pool_size = (2, 2)
    stride = 2

    T, Hc, Wc = original_tensor.shape
    row = (Hc - pool_size[0]) // stride + 1
    col = (Wc - pool_size[1]) // stride + 1

    output_tensor = torch.zeros((T, row, col, 4), device=device)

    for i in range(row):
        for j in range(col):
            region = original_tensor[
                :, i * stride : i * stride + pool_size[0],
                j * stride : j * stride + pool_size[1],
            ]  # [T,2,2]
            output_tensor[:, i, j] = region.reshape(T, 4)

    return output_tensor  # [T,row,col,4]


# =========================================================
# TRAINING: IQR-based thresholds (q1, lower_bound) - in memory
# =========================================================

def compute_thresholds_IQR(kernel_applied_result_in_diff_gray_image_overall,
                           kk=1.5,
                           device="cpu"):
    """
    Given a list of conv outputs [T,Hc,Wc], compute:
      - new_x: [T,row,col,4]
      - q1, lower_bound: [row,col]
    Returns them in memory (no txt I/O).
    """
    stacked = np.stack(kernel_applied_result_in_diff_gray_image_overall, axis=0)
    new_x = truncating_array_dynamic(stacked, device=device)  # [T,row,col,4]

    T, row, col, _ = new_x.shape
    x = new_x  # tensor on device

    lower_bound = torch.zeros((row, col), device=device)
    q1_for_future_use = torch.zeros((row, col), device=device)

    for i in range(row):
        for j in range(col):
            vals = x[:, i, j, :]  # [T,4]
            q1 = torch.quantile(vals, 0.25)
            q3 = torch.quantile(vals, 0.75)
            lb = q1 - kk * (q3 - q1)

            lower_bound[i, j] = lb
            q1_for_future_use[i, j] = q1

    return lower_bound.cpu().numpy(), q1_for_future_use.cpu().numpy()


# =========================================================
# Pooling & anomaly logic (CMAD decision part)
# =========================================================

def pooling(input_matrix, pool_height, pool_width,
            stride_height, stride_width, pool_type,
            device="cpu"):
    if pool_type == "max":
        input_matrix1 = torch.tensor(input_matrix, device=device)

        input_matrix2 = torch.where(input_matrix1 > 0, 0, input_matrix1)
        input_matrix3 = torch.abs(input_matrix2)

        input_tensor = input_matrix3.unsqueeze(0).unsqueeze(0)

        max_pool = nn.MaxPool2d(
            kernel_size=(pool_height, pool_width),
            stride=(stride_height, stride_width),
        )

        return_max = max_pool(input_tensor)[0][0].cpu().detach().numpy()
        return -1.0 * return_max

    elif pool_type == "mean":
        input_tensor = torch.tensor(input_matrix, device=device)
        input_tensor = input_tensor.unsqueeze(0).unsqueeze(0)

        mean_pool = nn.AvgPool2d(
            kernel_size=(pool_height, pool_width),
            stride=(stride_height, stride_width),
        )

        return mean_pool(input_tensor)[0][0].cpu().detach().numpy()


def anomaly_mask_for_pair(
    matrix,
    total_std,
    q1,
    gray_image_list,
    combined_indices,
    index,
    device="cpu",
):
    """
    Core of optimalSolution, but:
    - only computes anomaly_discord
    - returns mask [H,W] as numpy
    - no folder/file saving
    """
    r, c = 2, 2

    # pooling on conv result
    max_pooled = pooling(
        matrix,
        pool_height=r,
        pool_width=c,
        stride_height=r,
        stride_width=c,
        pool_type="max",
        device=device,
    )
    mean_pooled = pooling(
        matrix,
        pool_height=r,
        pool_width=c,
        stride_height=r,
        stride_width=c,
        pool_type="mean",
        device=device,
    )

    row, col = mean_pooled.shape

    # Dynamic padded size
    gray_next = file_to_gray(gray_image_list, index + 1, device=device)
    gray_prev = file_to_gray(gray_image_list, index, device=device)
    diff_img = gray_next - gray_prev  # [H+2, W+2]

    H_pad, W_pad = diff_img.shape

    # anomaly_discord
    anomaly_discord_array = torch.zeros(H_pad, W_pad, device=device)

    for i in range(row):
        for j in range(col):
            if max_pooled[i, j] < total_std[i, j]:
                if (mean_pooled[i, j] / max_pooled[i, j]) > (q1[i, j] / total_std[i, j]):
                    getIndices_anomaly = getIndices_in_orginal_gray(i, j, combined_indices)
                    for (rowIndex, colIndex) in getIndices_anomaly:
                        # Only mark as anomaly if diff < 0
                        if diff_img[rowIndex, colIndex] < 0:
                            anomaly_discord_array[rowIndex, colIndex] = 1

    anomaly_discord_array = anomaly_discord_array[1:-1, 1:-1]  # remove padding
    return anomaly_discord_array.cpu().numpy()  # [H,W]


# =========================================================
# CMAD class
# =========================================================

class CMAD:
    """
    CMAD model that reproduces your script logic,
    but:
      - thresholds kept in memory (no txt files),
      - can work on image folders OR generic arrays,
      - returns anomaly_masks as numpy [T-1,H,W].
    """

    def __init__(self, device=None, kk=1.5):
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self.device = device
        self.kk = kk

        self.total_std = None   # lower bound
        self.q1 = None
        self.combined_indices = None
        self.H = None
        self.W = None

    # -----------------------
    # TRAINING from images
    # -----------------------
    def fit_from_image_years(self, years):
        """
        years: iterable of folder names like ["2000", "2001", ...]
        Each folder should contain PNGs as in your original code.

        This matches your training loop exactly, but keeps thresholds in memory.
        """
        kernel_applied_overall = []

        first_H, first_W = None, None

        for year in years:
            filelist = glob.glob(f"{year}/*.png")
            filelist.sort()
            print(f"[IQR stage] Year {year}, files: {len(filelist)}")

            if len(filelist) < 2:
                continue

            gray_image_list, _ = rgb_to_gray_image_conversion(filelist, device=self.device)

            if first_H is None and len(gray_image_list) > 0:
                first_H, first_W = gray_image_list[0].shape

            diff_gray_list, diff_kernel_list = get_diff_gray_image_kernel_list(
                gray_image_list, device=self.device
            )

            temp_arr = get_kernel_applied_result_in_diff_gray_image(
                diff_gray_list, diff_kernel_list, device=self.device
            )
            print("  kernel_applied_result shape for year:", np.array(temp_arr).shape)

            kernel_applied_overall += list(temp_arr)

        if first_H is None:
            raise RuntimeError("No images found in any training year.")

        # build combined indices once
        self.H, self.W = first_H, first_W
        self.combined_indices = build_combined_indices_dynamic(first_H, first_W)

        print("Total diff frames in overall:", len(kernel_applied_overall))
        print("IQR multiplier (kk):", self.kk)

        self.total_std, self.q1 = compute_thresholds_IQR(
            kernel_applied_overall,
            kk=self.kk,
            device=self.device,
        )
        print("CMAD training (image years) complete.")
        return self

    # -----------------------
    # TRAINING from generic array
    # -----------------------
    def fit_from_array(self, X):
        """
        X: numpy array or torch tensor of shape [T,H,W]
           Generic spatio-temporal 2D data.
        """
        if isinstance(X, np.ndarray):
            X = torch.tensor(X, dtype=torch.float32, device=self.device)
        else:
            X = X.to(self.device).float()

        T, H, W = X.shape
        if T < 2:
            raise ValueError("Need at least 2 time steps for training.")

        self.H, self.W = H, W
        self.combined_indices = build_combined_indices_dynamic(H, W)

        diff_list, kernel_list = get_diff_list_from_array(X, device=self.device)

        conv_results = get_kernel_applied_result_in_diff_gray_image(
            diff_list, kernel_list, device=self.device
        )

        self.total_std, self.q1 = compute_thresholds_IQR(
            conv_results,
            kk=self.kk,
            device=self.device,
        )
        print("CMAD training (array) complete.")
        return self

    # -----------------------
    # PREDICTION from images
    # -----------------------
    def predict_from_image_year(self, year_folder, save_txt=False, out_dir=None):
        """
        year_folder: e.g. "2022"
        Returns anomaly_masks [T-1,H,W] as numpy.

        This mirrors your detection loop for one year,
        but returns masks instead of just saving txt.
        """
        if self.total_std is None or self.q1 is None:
            raise RuntimeError("Call fit_* before predict_*.")

        filelist = glob.glob(f"{year_folder}/*.png")
        filelist.sort()

        print(f"[CMAD stage] Year {year_folder}, files: {len(filelist)}")

        if len(filelist) < 2:
            raise ValueError("Need at least 2 images for detection.")

        gray_image_list, _ = rgb_to_gray_image_conversion(filelist, device=self.device)
        diff_gray_list, diff_kernel_list = get_diff_gray_image_kernel_list(
            gray_image_list, device=self.device
        )

        conv_results = get_kernel_applied_result_in_diff_gray_image(
            diff_gray_list, diff_kernel_list, device=self.device
        )

        anomaly_masks = []

        for i, matrix in enumerate(conv_results):
            mask = anomaly_mask_for_pair(
                matrix,
                self.total_std,
                self.q1,
                gray_image_list,
                self.combined_indices,
                index=i,
                device=self.device,
            )
            anomaly_masks.append(mask)

            if save_txt and out_dir is not None:
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                np.savetxt(
                    os.path.join(out_dir, f"anomaly_t{i}_t{i+1}.txt"),
                    mask,
                    delimiter="\t",
                    fmt="%d",
                )

        anomaly_masks = np.stack(anomaly_masks, axis=0)  # [T-1,H,W]
        return anomaly_masks

    # -----------------------
    # PREDICTION from array
    # -----------------------
    def predict_from_array(self, X, save_txt=False, out_dir=None):
        """
        X: numpy array or torch tensor [T,H,W]
        Returns anomaly_masks [T-1,H,W].
        """
        if self.total_std is None or self.q1 is None:
            raise RuntimeError("Call fit_* before predict_*.")

        if isinstance(X, np.ndarray):
            X = torch.tensor(X, dtype=torch.float32, device=self.device)
        else:
            X = X.to(self.device).float()

        T, H, W = X.shape
        if T < 2:
            raise ValueError("Need at least 2 time steps for prediction.")
        if H != self.H or W != self.W:
            raise ValueError(f"Input shape ({H},{W}) does not match training ({self.H},{self.W}).")

        # Build "gray_image_list" directly from X (same as images path)
        gray_image_list = [X[t] for t in range(T)]

        # We still need diff & kernels to get conv_results
        diff_list, kernel_list = get_diff_list_from_array(X, device=self.device)
        conv_results = get_kernel_applied_result_in_diff_gray_image(
            diff_list, kernel_list, device=self.device
        )

        anomaly_masks = []
        for i, matrix in enumerate(conv_results):
            mask = anomaly_mask_for_pair(
                matrix,
                self.total_std,
                self.q1,
                gray_image_list,
                self.combined_indices,
                index=i,
                device=self.device,
            )
            anomaly_masks.append(mask)

            if save_txt and out_dir is not None:
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                np.savetxt(
                    os.path.join(out_dir, f"anomaly_t{i}_t{i+1}.txt"),
                    mask,
                    delimiter="\t",
                    fmt="%d",
                )

        anomaly_masks = np.stack(anomaly_masks, axis=0)
        return anomaly_masks

