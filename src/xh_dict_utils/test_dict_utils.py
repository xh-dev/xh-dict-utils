import unittest

from dict_utils import Entries, Selector


class Testing(unittest.TestCase):
    def test_1(self):
        # for t in flatten({"a": 1, "b": [{"ba": 1}, {"bb": 2}, ["x", "y", "z"]]}):
        #     print(t)
        self.assertEqual(
            ["", "a", "b.[*]", "b.[0]", "b.[0].ba", "b.[1]", "b.[1].bb", "b.[2].[*]", "b.[2].[0]", "b.[2].[1]",
             "b.[2].[2]"],
            [t.get_selector() for t in Entries.from_dict({"a": 1, "b": [{"ba": 1}, {"bb": 2}, ["x", "y", "z"]]})],
        )

    def test_2(self):
        selector = Selector.from_notation("a.b.c")
        self.assertEqual(selector.depth(), 3, msg="test depth")
        self.assertEqual(selector.is_root(), False, msg="test is_root")
        self.assertEqual(selector.is_not_root(), True, msg="test is_not_root")
        self.assertEqual(selector.object_or_value("d").selector_str, "a.b.c.d")
        self.assertEqual(selector.is_array(), False, msg="test is_array")
        self.assertEqual(selector.is_array_group(), False, msg="test is_array_group")
        self.assertEqual(selector.is_array_item(), False, msg="test is_array_item")
        self.assertEqual(selector.is_object_or_value(), True, msg="test is_object_or_value")
        with self.assertRaises(Exception):
            selector.get_array_index()
        self.assertEqual(selector.list_group().selector_str, "a.b.c.[*]")
        self.assertEqual(selector.list(7).selector_str, "a.b.c.[7]")

    def test_3(self):
        print(Entries.from_dict({"a": 1, "b": [{"ba": 1}, {"bb": 2}, {"ba": 2}, ["x", "y", "z"]]}))

    def test_4(self):
        d = Entries.from_dict({"a": 1, "b": [{"ba": 1}, {"bb": 2}, {"ba": 2}, ["x", "y", "z"]]})

        # selector = d.exact_selector("b.[*]")
        # print("exact_selector('b.[*]')", selector)
        #
        # selector = d.exact_selector("b.[*].ba")
        # print("exact_selector('b.[*].ba')", selector)

        self.assertEqual(
            [
                "Entry(b.[*], [{'ba': 1}, {'bb': 2}, {'ba': 2}, ['x', 'y', 'z']])",
                "Entry(b.[0], {'ba': 1})",
                "Entry(b.[0].ba, 1)",
                "Entry(b.[1], {'bb': 2})",
                "Entry(b.[1].bb, 2)",
                "Entry(b.[2], {'ba': 2})",
                "Entry(b.[2].ba, 2)",
                "Entry(b.[3].[*], ['x', 'y', 'z'])",
                "Entry(b.[3].[0], x)",
                "Entry(b.[3].[1], y)",
                "Entry(b.[3].[2], z)"
            ]
            ,
            [str(i) for i in d.match_notation("b.[*]").asGenerator()]
        )

        self.assertEqual(
            [
                "Entry(b.[*], [{'ba': 1}, {'bb': 2}, {'ba': 2}, ['x', 'y', 'z']])"
            ]
            ,
            [str(i) for i in d.match_exact("b.[*]").asGenerator()]
        )

        self.assertEqual(
            ['Entry(b.[0].ba, 1)', 'Entry(b.[2].ba, 2)'],
            [str(i) for i in d.match_notation("b.[*].ba").asGenerator()]
        )

        self.assertEqual(
            [],
            [str(i) for i in d.match_exact("b.[*].ab").asGenerator()]
        )

        self.assertEqual(
            [
                "Entry(b.[0], {'ba': 1})",
                "Entry(b.[0].ba, 1)",
                "Entry(b.[3].[0], x)",
            ],
            [str(i) for i in d.match_regex(".*\\.\\[0].*").asGenerator()]
        )
        