class Node:
    """
    data: dictionary of {x,y,z} coordinates
    point_id: index position of the point in the pcd data
    """
    def __init__(self, data, point_id):
        self.point = {"X": data[0], "Y": data[1], "Z": data[2]}
        self.point_id = point_id
        self.left_node = None
        self.right_node = None