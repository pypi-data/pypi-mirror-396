# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Support for Parzzley configuration XML files.
"""
# pylint: disable=c-extension-no-member
import lxml.etree

import parzzley.config
from parzzley.config.file_formats import (
    register_file_format as _register_file_format,
    FileFormat as _FileFormat,
    timedelta,
)


@_register_file_format("xml")
class XmlFileFormat(_FileFormat):
    """
    XML file format.
    """

    def parse_file(self, config_file):

        xtree = lxml.etree.parse(config_file)
        xml_root = xtree.getroot()

        if xml_root.tag == "{urn:parzzley}Volume":
            return self.__sync_volume(xml_root, config_file)
        if xml_root.tag == "{urn:parzzley}Logging":
            return self.__logging(xml_root, config_file)
        raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

    def __sync_volume(self, xml_elem: lxml.etree.Element, config_file) -> "parzzley.config.Volume":
        sites = []
        aspects = []
        arguments = dict(xml_elem.attrib)
        name = arguments.pop("name")
        interval = timedelta(arguments.pop("interval", "5m"))
        if arguments:
            raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        for xml_root_elem in xml_elem.getchildren():
            if xml_root_elem.tag == "{urn:parzzley}Site":
                sites.append(self.__sync_site(xml_root_elem, config_file))
            elif xml_root_elem.tag.startswith("{urn:parzzley:aspects}"):
                aspects.append(self.__sync_aspects(xml_root_elem))
            else:
                raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        return parzzley.config.Volume(name, sites=sites, aspects=aspects, interval=interval)

    def __sync_site(self, xml_elem: lxml.etree.Element, config_file) -> "parzzley.config.Site":
        arguments = dict(xml_elem.attrib)
        name = arguments.pop("name")
        kind = arguments.pop("kind", "local")
        warn_after_str = arguments.pop("warn_after", "30d")
        warn_after = timedelta(warn_after_str) if warn_after_str else None
        aspects = []

        for xml_child_elem in xml_elem.getchildren():
            if xml_child_elem.tag.startswith("{urn:parzzley:aspects}"):
                aspects.append(self.__sync_aspects(xml_child_elem))
            else:
                raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        return parzzley.config.Site(name, kind=kind, arguments=arguments, aspects=aspects, warn_after=warn_after)

    def __sync_aspects(self, xml_elem: lxml.etree.Element) -> "parzzley.config.Aspect":
        type_name = xml_elem.tag.split("}")[1]

        return parzzley.config.Aspect(type_name=type_name, arguments=dict(xml_elem.attrib))

    def __logging(self, xml_elem: lxml.etree.Element, config_file) -> "parzzley.config.Logging":
        arguments = dict(xml_elem.attrib)
        min_severity = arguments.pop("min_severity", None)
        max_severity = arguments.pop("max_severity", None)
        if arguments:
            raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        formatter = None
        out = []
        exclude = []

        for xml_child_elem in xml_elem.getchildren():
            if xml_child_elem.tag == "{urn:parzzley}Formatter":
                if formatter:
                    raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")
                formatter = self.__log_formatter(xml_child_elem)
            elif xml_child_elem.tag == "{urn:parzzley}Out":
                out.append(self.__logger_out(xml_child_elem))
            elif xml_child_elem.tag == "{urn:parzzley}Exclude":
                exclude.append(self.__logger_exclusion(xml_child_elem, config_file))
            else:
                raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        if not formatter:
            raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")

        return parzzley.config.Logging(
            min_severity=min_severity, max_severity=max_severity, formatter=formatter, out=out, exclude=exclude
        )

    def __log_formatter(self, xml_elem: lxml.etree.Element) -> "parzzley.config.Logging.Formatter":
        arguments = dict(xml_elem.attrib)
        kind = arguments.pop("kind")
        return parzzley.config.Logging.Formatter(kind=kind, arguments=arguments)

    def __logger_out(self, xml_elem: lxml.etree.Element) -> "parzzley.config.Logging.Out":
        arguments = dict(xml_elem.attrib)
        kind = arguments.pop("kind")
        return parzzley.config.Logging.Out(kind=kind, arguments=arguments)

    def __logger_exclusion(self, xml_elem: lxml.etree.Element, config_file) -> "parzzley.config.Logging.Exclude":
        return parzzley.config.Logging.Exclude(
            conditions=(
                self.__logger_exclusion_condition(xml_child_elem, config_file)
                for xml_child_elem in xml_elem.getchildren()
            )
        )

    def __logger_exclusion_condition(
        self, xml_elem: lxml.etree.Element, config_file
    ) -> "parzzley.config.Logging.Exclude.BaseCondition":
        if xml_elem.tag == "{urn:parzzley}Condition":
            return parzzley.config.Logging.Exclude.Condition(arguments=dict(xml_elem.attrib))

        if xml_elem.tag == "{urn:parzzley}ConditionNegate":
            conditions = tuple(
                self.__logger_exclusion_condition(xml_child_elem, config_file)
                for xml_child_elem in xml_elem.getchildren()
            )
            if len(conditions) != 1:
                raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")
            return parzzley.config.Logging.Exclude.NegateCondition(condition=conditions[0])

        if xml_elem.tag in ("{urn:parzzley}ConditionAllOf", "{urn:parzzley}ConditionAnyOf"):
            if dict(xml_elem.attrib):
                raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")
            combination = "AND" if xml_elem.tag == "{urn:parzzley}ConditionAllOf" else "OR"
            conditions = (
                self.__logger_exclusion_condition(xml_child_elem, config_file)
                for xml_child_elem in xml_elem.getchildren()
            )
            return parzzley.config.Logging.Exclude.CombinedCondition(combination=combination, conditions=conditions)

        raise RuntimeError(f"invalid Parzzley config xml file: {config_file}")
