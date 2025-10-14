# world_server/resource_manager.py

class ResourceManager:
    """
    管理世界中的资源生产和消耗。
    这是一个静态类，因为我们不需要它的多个实例。
    """

    @staticmethod
    def produce(location, world_state):
        """
        在指定地点生产资源。
        :param location: 发生生产的地点对象。
        :param world_state: 当前的世界状态（包含所有地点）。
        """
        if location.get('produces') and location['state'] == 'active':
            resource_type = location['produces']
            rate = location.get('produces_rate', 1)

            # 在地点的库存中增加资源
            if resource_type not in location['inventory']:
                location['inventory'][resource_type] = 0
            location['inventory'][resource_type] += rate

            # print(f"Location '{location['name']}' produced {rate} {resource_type}. New total: {location['inventory'][resource_type]}")
        return True

    @staticmethod
    def consume(location, resource_type, amount, world_state):
        """
        在指定地点消耗资源。
        :param location: 发生消耗的地点对象。
        :param resource_type: 要消耗的资源类型。
        :param amount: 要消耗的数量。
        :param world_state: 当前的世界状态。
        :return: 如果成功消耗则返回True，否则返回False。
        """
        if location['state'] == 'active' and resource_type in location['inventory'] and location['inventory'][resource_type] >= amount:
            location['inventory'][resource_type] -= amount
            # print(f"Consumed {amount} {resource_type} from '{location['name']}'. Remaining: {location['inventory'][resource_type]}")

            # 如果资源耗尽，可以改变地点的状态
            if location['inventory'][resource_type] <= 0:
                location['state'] = 'depleted'
                # print(f"'{location['name']}' has been depleted of {resource_type}.")
            return True
        return False

    @staticmethod
    def get_richest_location(resource_type, locations):
        """
        查找拥有特定资源且库存最丰富的地点。
        :param resource_type: 需求的资源类型。
        :param locations: 所有地点的列表。
        :return: 最合适的地点对象，如果没有则返回None。
        """
        best_location = None
        max_amount = 0

        # 筛选出所有提供所需资源且处于激活状态的地点
        valid_locations = [
            loc for loc in locations
            if loc['state'] == 'active' and resource_type in loc.get('inventory', {}) and loc['inventory'][resource_type] > 0
        ]

        if not valid_locations:
            return None

        # 从有效地点中找到库存最多的那个
        best_location = max(valid_locations, key=lambda loc: loc['inventory'][resource_type])

        return best_location