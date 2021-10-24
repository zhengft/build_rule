#!/usr/bin/env python3

from typing import List, NamedTuple, Tuple
from pathlib import Path

from lxml import etree


class BuildRule(NamedTuple):
    """构建规则。"""
    productname: str
    added_contition: str
    addname: str
    target: str

    @classmethod
    def parse(cls, rule_ele):
        """解析构建规则元素。"""
        productname = rule_ele.attrib['productname']
        added_contition = rule_ele.attrib['added_contition']
        addname = rule_ele.attrib['addname']
        target = rule_ele.attrib['target']
        return cls(productname, added_contition, addname, target)

    def to_element(self) -> Tuple[bool, etree.Element]:
        """转换为XML元素。"""
        rule_ele = etree.Element('rule')
        rule_ele.attrib['productname'] = self.productname
        rule_ele.attrib['added_contition'] = self.added_contition
        rule_ele.attrib['addname'] = self.addname
        rule_ele.attrib['target'] = self.target
        return True, rule_ele


class BuildGroup(NamedTuple):
    """构建规则组。"""
    name: str
    weight: str
    producttype: str
    rules: List[BuildRule]

    @classmethod
    def parse(cls, buildgroup_ele):
        """解析构建规则组元素。"""
        name = buildgroup_ele.attrib['name']
        weight = buildgroup_ele.attrib['weight']
        producttype = buildgroup_ele.attrib['producttype']
        rules = []
        for rule_ele in buildgroup_ele:
            rule = BuildRule.parse(rule_ele)
            rules.append(rule)
        return cls(name, weight, producttype, rules)

    def to_element(self) -> Tuple[bool, etree.Element]:
        """转换为XML元素。"""
        buildgroup_ele = etree.Element('buildgroup')
        buildgroup_ele.attrib['name'] = self.name
        buildgroup_ele.attrib['weight'] = self.weight
        buildgroup_ele.attrib['producttype'] = self.producttype
        
        for rule in self.rules:
            ret, rule_ele = rule.to_element()
            if not ret:
                return False, None
            buildgroup_ele.append(rule_ele)
        
        return True, buildgroup_ele


class BuildRuleFile(NamedTuple):
    """构建规则文件。"""
    version: str
    buildgroups: List[BuildGroup]

    @classmethod
    def parse(cls, filepath):
        """解析构建规则文件。"""
        tree = etree.parse(filepath)
        root = tree.getroot()
        version_ele = root[0]
        version = version_ele.tag.lower()

        buildgroups = []
        for buildgroup_ele in version_ele:
            buildgroup = BuildGroup.parse(buildgroup_ele)
            buildgroups.append(buildgroup)

        return cls(version, buildgroups)

    def to_element(self) -> Tuple[bool, etree.Element]:
        """转换为XML元素。"""
        root_ele = etree.Element('BUILD_RULE')
        version_ele = etree.SubElement(root_ele, self.version.upper())
        for buildgroup in self.buildgroups:
            ret, buildgroup_ele = buildgroup.to_element()
            if not ret:
                return False, None
            version_ele.append(buildgroup_ele)
        return True, root_ele

    def write(self, filepath: str) -> bool:
        """输出XML文件。"""
        ret, root_ele = self.to_element()
        if not ret:
            return False
        tree = etree.ElementTree(root_ele)
        tree.write(filepath, pretty_print=True)
        return True


def main():
    brfile = BuildRuleFile.parse('turing.xml')
    print(brfile)
    brfile.write('turing.xml')


if __name__ == '__main__':
    main()
