# ==================================================================== #
# File name: bbox.py
# Author: Long H. Pham and Duong N.-N. Tran
# Date created: 03/27/2021
#
# Implements common operations on label.
# ==================================================================== #
from typing import *

from munch import Munch


# MARK: - Get label

def get_label(
	labels   : List[Dict],
	name     : Optional[str] = None,
	id       : Optional[int] = None,
	train_id : Optional[int] = None,
) -> Optional[Dict]:
	"""

	Args:
		labels (list):
			The list of all labels' dicts.
		name (str):
			The label's name to search from ``labels``.
		id (int):
			The label's id to search from ``labels``.
		train_id (int):
			The label's train id to search from ``labels``.

	Returns:
		label (Dict, Optional):
			The label dict.
	"""
	for label in labels:
		if (name is not None) and hasattr(label, "name") and (name == label.name):
			return label
		
		if (id is not None) and hasattr(label, "id") and (id == label.id):
			return label
		
		if (train_id is not None) and hasattr(label, "train_id") and (train_id == label.train_id):
			return label
			
	return None


def get_majority_label(object_labels: List[Dict]) -> Dict:
	"""Get the most popular label of the road_objects.
	
	Args:
		object_labels (list):
			The list of object's labels.
	
	Returns:
		label (dict):
			The label that has max appearances.
	"""
	# TODO: Count number of appearance of each label.
	unique_labels = Munch()
	label_voting  = Munch()
	for label in object_labels:
		key   = label.id
		value = label_voting.get(key)
		if value:
			label_voting[key]  = value + 1
		else:
			unique_labels[key] = label
			label_voting[key]  = 1
			
	# TODO: get key (label's id) with max value
	max_id = max(label_voting, key=label_voting.get)
	return unique_labels[max_id]