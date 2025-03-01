""" Common utility functions for BBO Chat."""


def build_text_list(data: list[str]) -> list[str]:
    return [u'{unicodes_value}'.format(unicodes_value=item)
            for item in data if item and item[0] != '#']
