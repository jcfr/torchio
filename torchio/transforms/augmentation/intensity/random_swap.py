
import numpy as np
from ....utils import is_image_dict, to_tuple
from ....torchio import DATA, INTENSITY
from ....data.sampler.sampler import get_random_indices_from_shape, crop
from .. import RandomTransform


class RandomSwap(RandomTransform):
    def __init__(
            self,
            patch_size=15,
            num_iterations=100,
            seed=None,
            verbose=False,
            ):
        super().__init__(seed=seed, verbose=verbose)
        self.patch_size = to_tuple(patch_size)
        self.num_iterations = num_iterations

    @staticmethod
    def get_params():
        # TODO
        return

    def apply_transform(self, sample):
        for image_dict in sample.values():
            if not is_image_dict(image_dict):
                continue
            if image_dict['type'] != INTENSITY:
                continue
            swap(image_dict[DATA][0], self.patch_size, self.num_iterations)
        return sample


def swap(tensor, patch_size, num_iterations):
    patch_size = to_tuple(patch_size)
    for _ in range(num_iterations):
        first_ini, first_fin = get_random_indices_from_shape(
            tensor.shape,
            patch_size,
        )
        while True:
            second_ini, second_fin = get_random_indices_from_shape(
                tensor.shape,
                patch_size,
            )
            if np.all(second_ini >= first_ini) and np.all(second_fin <= first_fin):
                continue  # patches overlap
            else:
                break  # patches don't overlap
        first_patch = crop(tensor, first_ini, first_fin)
        second_patch = crop(tensor, second_ini, second_fin).clone()
        insert(tensor, first_patch, second_ini)
        insert(tensor, second_patch, first_ini)


def insert(tensor, patch, index_ini):
    index_fin = index_ini + np.array(patch.shape)
    i_ini, j_ini, k_ini = index_ini
    i_fin, j_fin, k_fin = index_fin
    tensor[i_ini:i_fin, j_ini:j_fin, k_ini:k_fin] = patch