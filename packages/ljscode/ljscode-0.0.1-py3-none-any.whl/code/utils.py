import os
import pickle
import h5py
from datetime import datetime
import numpy as np
from itertools import chain
from typing import Dict, Tuple, Hashable, Iterable, Optional
from pathlib import Path
from scipy.linalg import svd

def pca_svd(data, n_components: Optional[int]=None, pre_center: bool=True):
    """
    使用 SciPy 的 SVD 实现 PCA。

    Parameters
    ----------
    data : ndarray
        输入数据，形状为 (n_samples, n_features)。
    pre_center : bool
        是否减去均值
    n_components : int or None
        要保留的主成分数量，默认为所有主成分。

    Returns
    -------
    data_i : ndarray
        预处理后的数据，用于 SVD。
    pc2run : ndarray
        主成分方向向量（载荷矩阵），形状为 (n_features, n_components)
    scores : ndarray
        主成分得分矩阵（每个样本在主成分方向上的投影），形状为 (n_samples, n_components)
    variances : ndarray
        每个主成分的方差。
    """

    X = np.asarray(data, dtype=np.float64)
    n_samples, n_features = X.shape

    # === 1. 数据预处理 ===
    if pre_center:
        data_i = X - X.mean(axis=0)
    else:
        data_i = X.copy()

    # === 2. SVD 分解 ===
    # X = U * S * Vt
    U, S, Vh = svd(data_i, full_matrices=False)
    S = np.atleast_1d(S)
    U, Vt = np.asarray(U), np.asarray(Vh)
    total_var = np.sum(S ** 2)

    # === 3. 选择主成分数量 ===
    if n_components is not None:
        U = U[:, :n_components]
        S = S[:n_components]
        Vt = Vt[:n_components, :]
    
    # === 4. Explained Variance ratio ===
    exp_var = (S**2) / total_var

    return data_i, np.asarray(U), np.asarray(S), np.asarray(Vt), exp_var

def list_files(directory, keywords, nested_folder=True):
    """
    List all files in the specified directory that contain all given keywords in their names.
    
    Args:
        directory (str): The directory to search in.
        keywords (list): A list of strings to search for in file names.
        
    Returns:
        list: A list of Path objects that match the criteria.
    """
    # Create a Path object for the specified directory
    path = Path(directory)
    
    # Use a list comprehension to find all files that contain all keywords
    if nested_folder:
        matching_files = [
            file for file in path.rglob("*")
            if file.is_file() and all(keyword in file.name for keyword in keywords)
        ]
    else:
        matching_files = [
            file for file in path.iterdir()
            if file.is_file() and all(keyword in file.name for keyword in keywords)
        ]
    
    return matching_files

def frequent_items(
    groups: Iterable,
    min_freq: int=10,
) -> np.ndarray:
    """
    Aggregate multiple sequences, count element frequencies,
    and return the elements that occur more than `min_freq` times.

    Parameters
    ----------
    groups : Sequence[Iterable]
        A collection of one-dimensional iterables (lists, tuples, 1-D ndarrays, …).
        Each iterable can contain any hashable elements (e.g., feature indices).
    min_freq : int
        Frequency threshold. Only elements whose total count exceeds this value
        are returned.

    Returns
    -------
    np.ndarray
        Sorted array of unique elements whose frequency is greater than
        `min_freq`.
    """
    # Flatten all subsequences into a single list
    flattened = list(chain.from_iterable(groups))

    # Count unique values and their frequencies
    values, counts = np.unique(flattened, return_counts=True)

    # Keep elements whose frequency is above the threshold
    return values[counts >= min_freq]

def global_index_from_key_offset(key: Hashable,  
                                 local_index: int,  
                                 counts_per_key: Dict[Hashable, int]  
                                 ) -> int:  
    """  
    Convert (key, local_index) to the corresponding global index in the  
    flattened ordering of all items.  

    The flattened ordering is defined by iterating over `counts_per_key`  
    in its natural iteration order.

    Parameters  
    ----------  
    key : Hashable  
        The group that contains the item.
    local_index : int
        Zero-based position of the item within that group.
    counts_per_key : Dict[Hashable, int]  
        A dictionary whose keys label groups and whose values give the number  
        of items in each group.  

    Returns  
    -------  
    int  
        The zero-based index the item would have if every group were laid  
        out one after another.  

    Raises  
    ------  
    KeyError  
        If `key` is not present in `counts_per_key`.  
    ValueError  
        If `local_index` is negative or not smaller than the group’s size.  

    Examples  
    --------  
    >>> counts = {'A': 3, 'B': 2, 'C': 4}  # total 9 items  
    >>> global_index_from_key_offset('B', 1, counts)  
    4     # second item of 'B' is the 5th item overall (index 4)  
    """  
    if key not in counts_per_key:  
        raise KeyError(f"{key!r} is not a valid group key")  

    group_size = counts_per_key[key]  
    if not (0 <= local_index < group_size):  
        raise ValueError(  
            f"local_index {local_index} is out of bounds for key {key!r} "  
            f"(valid range: 0–{group_size - 1})"  
        )  

    # Sum the sizes of all groups that appear *before* the target key  
    prior_items = 0  
    for k, count in counts_per_key.items():  
        if k == key:  
            break  
        prior_items += count  

    return prior_items + local_index  

def locate_key_and_offset(global_index: int,
                          counts_per_key: Dict[Hashable, int]
                          ) -> Tuple[Hashable, int]:
    """  
    Map a single zero-based position in a flattened view of all items  
    to the (key, local_index) pair inside its original group.  

    Parameters  
    ----------  
    global_index : int  
        Zero-based overall position (0 means “first item overall”).  
    counts_per_key : Dict[Hashable, int]  
        A dictionary whose keys identify groups and whose values tell how many  
        items each group contains.  

    Returns  
    -------  
    key : Hashable  
        The group that contains the requested item.  
    local_index : int  
        Position of that item within its own group (also zero-based).  

    Raises  
    ------  
    ValueError  
        If `global_index` is negative or larger than the total number of  
        items implied by `counts_per_key`.  

    Examples  
    --------  
    >>> counts = {'A': 3, 'B': 2, 'C': 4}   # total 9 items  
    >>> locate_key_and_offset(5, counts)  
    ('C', 0)   # 6th item overall is the 1st item inside key 'C'  
    """

    if global_index < 0:
        raise ValueError("global_index must be non-negative")

    cumulative = 0
    for key, count in counts_per_key.items():
        cumulative += count
        if cumulative > global_index:
            local_index = global_index - (cumulative - count)
            return key, local_index

    raise ValueError(f"global_index {global_index} exceeds total data size")

def find_indices_of_A_in_B(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """  
    Finds all indices in B whose rows match any row in A.  

    This function uses broadcasting to compare each row in B against all rows  
    in A. It is assumed that both A and B are 2D arrays of shape (?, 3).  

    Parameters  
    ----------  
    A : np.ndarray  
        A 2D array of shape (n, 3) containing reference rows.  
    B : np.ndarray  
        A 2D array of shape (m, 3) in which we look for rows that match those in A.  

    Returns  
    -------  
    np.ndarray  
        A 1D array of sorted indices of B where each row matches a row in A.  
    """
    # Ensure both A and B are 2D arrays  
    if A.ndim != 2 or B.ndim != 2:  
        raise ValueError("Both A and B must be 2D arrays.")

    # Broadcast B to shape (m, 1, 3), so we compare each row in B against every row in A
    # After broadcasting, the comparison generates a boolean array of shape (m, n, 3).
    # Taking .all(-1) checks if all elements in the last axis (3 columns) match,
    # resulting in (m, n). Then .any(-1) reduces that to (m,), marking True
    # for any row in B that matches at least one row in A.

    return np.where((B[:, None, :] == A).all(axis=-1).any(axis=-1))[0]

def tile_mean_value(data: np.ndarray, axis: int, num_repeat: int) -> np.ndarray:  
    """
    Calculate the mean of a 1D NumPy array and tile it a specified number of times.

    Args:
        data (np.ndarray): A 1-dimensional array of numeric data.
        num_mean (int): The number of times to repeat (tile) the mean value.

    Returns:
        np.ndarray: An array where the mean value is repeated 'num_mean' times.
    """

    # Compute the mean along the given axis, preserving the axis dimension  
    mean_rate = np.mean(data, axis=axis, keepdims=True)  

    # Repeat (tile) mean_rate along the specified axis num_mean times  
    result = np.repeat(mean_rate, num_repeat, axis=axis)  
    return result

def tile_repeat_value(data: np.ndarray, axis: int, num_repeat: int, seed: int = 2025) -> np.ndarray:
    """  
    Repeat elements of a NumPy array along a specified axis so that its size along   
    that axis becomes exactly `num_repeat`. A random seed can be specified for   
    reproducible selection of leftover elements.  

    Args:  
        data (np.ndarray): The input NumPy array of any dimension.  
        axis (int): The axis along which the expansion in size should occur.  
        num_repeat (int): The target size for `data` along the specified axis.  
        seed (int, optional): A seed for the random number generator to allow   
            reproducible random sampling. Defaults to 2025.  

    Returns:  
        np.ndarray: A new array whose shape matches the original `data` except that   
                    its size along `axis` is `num_repeat`.  

    Raises:  
        ValueError: If the specified axis is out of range for the input array.  
    """  

    rng = np.random.default_rng(seed)

    original_size = data.shape[axis]
    factor = num_repeat // original_size
    remainder = num_repeat % original_size

    if remainder == 0:
        return np.repeat(data, factor, axis=axis)
    else:
        chosen_indices = rng.choice(range(original_size), remainder, replace=False)
        leftover_data = np.take(data, chosen_indices, axis=axis)
        repeated_data = np.repeat(data, factor, axis=axis)
        return np.concatenate([repeated_data, leftover_data], axis=axis)

def print_dict_struct(dict_data, date_format='%Y-%m-%d', indent_level=-1):
    """  
    Print the structure of a dictionary.  

    This function traverses the input dictionary, printing out the keys and their corresponding values.   
    If a key is a valid date in the specified format, it will be skipped in the printing process.   
    It identifies NumPy arrays and prints their shapes, while also indicating the type of other values.  

    Args:  
        dict_data (dict): The dictionary to process and print.  
        date_format (str): The date format to check against (default is '%Y-%m-%d').  
        indent_level (int): The current indentation level for nested dictionaries (default is -1).  

    Returns:  
        None  
    """
    skip = False
    indent_level += 1

    for key, value in dict_data.items():
        if skip:
            continue

        if isinstance(value, dict):
            print(f"{' ' * 2*indent_level}- {key}")
            print_dict_struct(value, date_format,
                              indent_level)  # Recursive call
        else:
            if isinstance(value, np.ndarray):
                print(
                    f"{' ' * 2*indent_level}- {key}: A Numpy array with shape {value.shape}")
            elif isinstance(value, (int,float)):
                print(
                    f"{' ' * 2*indent_level}- {key}: {value}")
            else:
                print(f"{' ' * 2*indent_level}- {key}: {type(value)}")

        def is_like_n_format(num_str: str) -> bool:
            if num_str.startswith("n") and num_str[1:].isdigit():
                return True
            return False

        try: 
            # Check if the key is int
            if isinstance(key, int):
                skip = True
                continue
            # Check if the key is a neuron index
            if is_like_n_format(str(key)):
                skip = True
                continue
            # Check if the key is a valid date format
            datetime.strptime(str(key), date_format)
            skip = True
        except ValueError:
            skip = False


def get_folder_list(data_root: str, folder_mark: str = "ocean") -> list:
    """
    Get a sorted list of data folders.

    Args:
        data_root (str): The root directory containing data folders.
        folder_mark (str): A string to identify relevant folders. Defaults to "ocean".

    Returns:
        list: A sorted list of folder names, from earliest to latest date.
    """
    file_list = os.listdir(data_root)
    data_folder_list = [name for name in file_list if folder_mark in name]
    data_folder_list.sort(
        key=lambda date: datetime.strptime(date, f"{folder_mark}%Y-%m-%d")
    )
    return data_folder_list


def concat_through_list(list_of_arrays):
    """Concatenates a list of NumPy arrays vertically (along axis 0).  

    Args:  
        list_of_arrays (list of numpy.ndarray): A list containing NumPy arrays to be concatenated.  
                                                 All arrays must be 2D and have the same number of columns.  
                                                 If the list is empty, returns None.  

    Returns:  
        numpy.ndarray: A NumPy array containing the vertical concatenation of all arrays in the input list.  
                       Returns None if the input list is empty.  

    """
    concatenated_array = np.array([])
    # Iterate through the list of arrays and concatenate
    for array in list_of_arrays:
        if concatenated_array.size == 0:
            # First array: initialize the concatenated array
            concatenated_array = array
        else:
            # Check for column consistency before concatenating
            if array.shape[1] != concatenated_array.shape[1]:
                raise ValueError(
                    "Arrays must have the same number of columns for vertical concatenation.")
            # Subsequent arrays: concatenate vertically (axis=0)
            concatenated_array = np.concatenate(
                (concatenated_array, array), axis=0)

    return concatenated_array


def group_contiguous(data_list: list, return_type: str = "value") -> list:
    """  
    Groups contiguous values or index from a sorted list of integers.  

    This function takes a sorted list of integers and groups consecutive numbers into subsets.  
    A group consists of numbers where each element is exactly 1 greater than its predecessor.  

    Args:  
        data_list (list[int]): A sorted list of integer indices.  
        return_type (str): which type data to return

    Returns:  
        nested list: A nested list with lists containing the contiguous data.  

    Example:  
        >>> indices = [1, 2, 3, 5, 6, 8]  
        >>> group_contiguous_indices(indices)  
        [[1, 2, 3], [5, 6], [8]]
    """
    last_value = None
    value_group = []
    index_group = []
    group_list_value = []
    group_list_index = []

    for i in data_list:
        if last_value is None:
            group_list_value.append(i)
            group_list_index.append(data_list.index(i))
        elif (i - last_value) == 1:
            group_list_value.append(i)
            group_list_index.append(data_list.index(i))
        else:
            value_group.append(group_list_value)
            group_list_value = [i]
            index_group.append(group_list_index)
            group_list_index = [data_list.index(i)]
        last_value = i

    # Add the final group if it's not empty
    if group_list_value:
        value_group.append(group_list_value)

    if return_type == "value":
        return value_group
    if return_type == "index":
        return index_group
    return []


def flatten_list(nested_list: list) -> list:
    """  
    Flattens a nested list using recursion.  

    Args:  
        nested_list: The nested list to flatten.  

    Returns:  
        A flattened list.  
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):  # Check if the item is a list
            # Recursively flatten the sublist
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened

def save_dict_as_pkl(
    file_name: str,
    data: dict,
    ):

    with open(f"{file_name}.pkl", "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_dict_from_pkl(
    file_name: str
    ):
    with open(f"{file_name}.pkl", "rb") as f:
        data = pickle.load(f)
    return data

def save_dict_to_hdf5(dic, h5file):
    """  
    递归地将 `dic`（一个可能嵌套的字典）写入到 h5file (h5py.Group)。  
    """
    for key, val in dic.items():
        # 如果值本身还是一个字典，则继续建立 group
        if isinstance(val, dict):
            subgroup = h5file.create_group(key)
            save_dict_to_hdf5(val, subgroup)
        else:
            # 将可转换为数组的数据创建 dataset
            # 例如：list、numpy array、标量等
            # 如果是字符串，可转成 np.string_ 或存成属性
            # 这里以直接存成数组为例
            h5file.create_dataset(key, data=val)


def load_hdf5_to_dict(h5group):
    """  
    递归将 h5group 中的层次结构读取为一个嵌套字典。  
    """
    out_dict = {}
    for key in h5group:
        item = h5group[key]
        if isinstance(item, h5py.Group):
            out_dict[key] = load_hdf5_to_dict(item)  # 继续深入
            if key == 'label_names':
                for seq_type in out_dict[key].keys():
                    out_dict[key][seq_type] = [i.decode("utf-8") for i in out_dict[key][seq_type]]
        else:
            # item 是一个 dataset
            out_dict[key] = item[()]  # 读取原始数据
            if key == 'lbs':
                out_dict[key] = [i.decode("utf-8") for i in out_dict[key]]
            
    return out_dict

def split_train_test_trials(selected_indices: list,
                            train_ratio: float = 0.6,
                            seed: int = 2025):
    """  
    Generate trial IDs for training and testing datasets.  

    This function randomly samples trial IDs from a list of selected indices into   
    training and testing sets based on a specified training ratio. The selection is   
    done without replacement, ensuring that the training and test sets are unique.  

    Parameters:  
    ----------  
    selected_indices : list  
        A list of trial IDs (indices) from which to sample.  

    train_ratio : float, optional, default=0.6  
        The proportion of trial IDs to allocate to the training set.   
        The training set will contain `train_ratio` percent of the `selected_indices`.  

    seed : int, optional, default=2025  
        A random seed for reproducibility of the random sampling.  

    Returns:  
    -------  
    train_ids_list : numpy.ndarray  
        An array of randomly sampled trial IDs allocated to the training set.  

    test_ids_list : numpy.ndarray  
        An array of trial IDs allocated to the testing set, which are not included in the training set.  

    Notes:  
    -----  
    - The function utilizes NumPy's random number generator for sampling and is designed to be   
      reproducible through the use of a seed value.  
    - Ensure that the length of `selected_indices` is greater than or equal to the number of  
      trials required for the training set, or an error will be raised due to insufficient  
      samples.  
    """

    rng = np.random.default_rng(seed)
    num_selected = len(selected_indices)

    if num_selected in (0, 1):
        raise ValueError("Not enough trials")
    if num_selected == 3:
        num_train = 2
    else:
        num_train = max(1, int(np.round(num_selected * train_ratio), 0))

    train_ids_list = rng.choice(
        selected_indices, size=num_train, replace=False)
    test_ids_list = np.setdiff1d(selected_indices, train_ids_list)

    return train_ids_list, test_ids_list

def set_relation(arr1: np.ndarray,
                 arr2: np.ndarray,
                 output_type: str = 'intersection',
                 universe: Optional[np.ndarray] = None):
    """
    Parameters
    ----------
    arr1, arr2 : 1-D 数值向量（元素将先被去重）
    output_type : str
        'intersection' → 同时出现在 arr1 和 arr2
        'arr1_only'    → 只在 arr1, 不在 arr2
        'arr2_only'    → 只在 arr2, 不在 arr1
        'none'         → 不在两者中的元素
                         (需要额外给出 universe)
    universe : 1-D 向量，可选
        仅当 output_type='none' 时必须提供，
        代表“全集”。
    """
    a = np.unique(arr1)
    b = np.unique(arr2)

    if output_type == 'intersection':
        return np.intersect1d(a, b)

    elif output_type == 'arr1_only':
        return np.setdiff1d(a, b)

    elif output_type == 'arr2_only':
        return np.setdiff1d(b, a)

    elif output_type == 'none':
        if universe is None:
            raise ValueError('要得到 "none" 结果必须提供 universe')
        u = np.unique(universe)
        return np.setdiff1d(u, np.union1d(a, b))

    else:
        raise ValueError(
            'output_type 只能是 '
            '"intersection", "arr1_only", "arr2_only", "none"'
        )