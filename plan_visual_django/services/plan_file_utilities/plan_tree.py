from anytree import Node, findall, RenderTree
from plan_visual_django.models import Plan, PlanActivity


class PlanActivityTreeNode(Node):
    def __init__(self, name, id:str=None, activity:PlanActivity=None, **kwargs):
        super().__init__(name, **kwargs)
        self.id: str = id
        self.activity: PlanActivity = activity


class PlanTree:
    """
    Creates a tree from an input plan.

    Relies on the fact that:
    - The activities in an imported plan are structured into a sequence which represents a hierarcical structure.
    - The relationship between activities is defined by the level, in that, while iterating activities in sequence
      order:
      - If the level of the next activity goes up by one the subsequent activity is a child of the current activity
      - If the level of the next activity is the same as the current one, the subsequent activity is a sibling of the
        current one.
      - If the level of the next activity goes down by one or more, it is a sibling of the most recent activity at the
        same level.
    """
    # Helper to avoid repeated code in accessing either node or activity in getter type functions
    accesor = lambda node, return_as_nodes: node if return_as_nodes else node.activity

    def __init__(self, plan: Plan):
        self.plan: Plan = plan
        self._parse_plan_to_tree()

    def get_root(self):
        if self.root is None:
            self._parse_plan_to_tree()
        return self.root

    def get_activity_list(self):
        """
        Returns flat list of activities in entry order (preserved within tree)
        :return:
        """
        return self._get_activity_list()

    def get_node_list(self):
        """
        Returns flat list of activities in entry order (preserved within tree)
        :return:
        """
        return self._get_activity_list(return_as_nodes=True)

    def get_plan_tree_activity_by_unique_id(self, unique_id: str):
        if self.root is None:
            self._parse_plan_to_tree()
        matching_node = self._get_node_for_id(unique_id)
        return matching_node.activity

    def get_plan_tree_node_by_unique_id(self, unique_id: str):
        if self.root is None:
            self._parse_plan_to_tree()
        matching_node = self._get_node_for_id(unique_id)
        return matching_node

    def get_plan_tree_child_activities_by_unique_id(self, unique_id: str):
        return self._get_children_by_unique_id(unique_id)

    def get_plan_tree_child_nodes_by_unique_id(self, unique_id: str):
        return self._get_children_by_unique_id(unique_id, return_as_nodes=True)

    def get_plan_tree_nodes_by_unique_id(self, unique_id: str):
        return self._get_children_by_unique_id(unique_id, return_as_nodes=True)

    def _get_activity_list(self, return_as_nodes: bool = False):
        """
        Get list of all activities in the tree but return either as activity records or nodes.

        :param return_as_nodes:
        :return:
        """
        if self.root is None:
            self._parse_plan_to_tree()

        return [PlanTree.accesor(activity_node, return_as_nodes) for activity_node in self.root.descendants]

    def _get_node_by_unique_id(self, unique_id, return_as_nodes: bool = False):
        if self.root is None:
            self._parse_plan_to_tree()

        matching_node = self._get_node_for_id(unique_id)
        return PlanTree.accesor(matching_node, return_as_nodes)

    def _get_children_by_unique_id(self, unique_id, return_as_nodes: bool = False):
        if self.root is None:
            self._parse_plan_to_tree()
        matching_node = self._get_node_for_id(unique_id)
        accesor = lambda node: node.activity if return_as_nodes else node
        activity_children = [PlanTree.accesor(node, return_as_nodes) for node in matching_node.children]

        return activity_children

    def print_plan_tree(self):
        for pre, _, node in RenderTree(self.root):
            print("%s%s" % (pre, node.name))

    def _parse_plan_to_tree(self):
        plan_activities = self.plan.planactivity_set.all()

        root = Node(name="ROOT", id="ROOT")
        current_node = root
        current_level = None

        for index, activity in enumerate(plan_activities, start=1):
            next_level = activity.level
            if index == 1:
                # Need to carry out some initialisation so that the logic works on the first element
                current_level = activity.level - 1
            # Work out which case this is and add to tree structure accordingly
            if next_level == current_level + 1:
                # This is a child activity, so add as sub-node
                activity_node = self._create_activity_node(parent=current_node, activity=activity)
            elif next_level == current_level:
                # This is a sibling so add to same parent
                activity_node = self._create_activity_node(parent=current_node.parent, activity=activity)
            elif next_level < current_level:
                # This activity is the sibling of an activity at a lower level
                # We have to find the parent at the right level to attach this sibling to
                num_levels = current_level - next_level + 1
                parent_node = current_node
                for level in range(num_levels):
                    parent_node = parent_node.parent
                activity_node = self._create_activity_node(parent=parent_node, activity=activity)
            else:
                raise Exception(f"Invalid level for activity {activity.activity_name:<20} at level {activity.level} ")

            current_level = next_level
            current_node = activity_node
        self.root = root

    def get_plan_tree_depth_by_unique_id(self, unique_id: str):
        if self.root is None:
            self._parse_plan_to_tree()

        matching_node = self._get_node_for_id(unique_id)
        return matching_node.depth


    def _create_activity_node(self, activity, parent):
        activity_node = PlanActivityTreeNode(name=activity.activity_name, parent=parent, id=activity.unique_sticky_activity_id, activity=activity)
        return activity_node

    def _get_node_for_id(self, unique_id: str):
        """
        Should only be one node for a given id, so find matching nodes and check that there is zero or one.
        """
        matches = findall(self.root, filter_=lambda n: n.id == unique_id)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            return None
        else:
            raise ValueError(f"More than one match found for unique id {unique_id} in plan")
