#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Configuration loader.
"""
import parzzley.config.file_formats
import parzzley.fs
import parzzley.sync.aspect
import parzzley.sync.logger.conditions


def load_volume(volume_config: "parzzley.config.Volume") -> "parzzley.sync.Volume":
    """
    Return a volume for a volume configuration.

    :param volume_config: The volume configuration.
    """
    return parzzley.sync.Volume(
        volume_config.name,
        [load_site_setup(site_config) for site_config in volume_config.sites],
        {
            site_config.name: tuple(
                load_aspect(aspect_config) for aspect_config in [*volume_config.aspects, *site_config.aspects]
            )
            for site_config in volume_config.sites
        },
    )


def load_site_setup(site_config: "parzzley.config.Site") -> "parzzley.fs.SiteSetup":
    """
    Return a site setup for a site configuration.

    :param site_config: The site configuration.
    """
    backend = parzzley.fs.backend_by_kind(site_config.kind)
    if backend is None:
        raise ValueError(f"unknown site kind: {site_config.kind}")
    return parzzley.fs.SiteSetup(site_config.name, backend, site_config.arguments)


def load_aspect(aspect_config: "parzzley.config.Aspect") -> "parzzley.sync.aspect.Aspect":
    """
    Return an aspect for an aspect configuration.

    :param aspect_config: The aspect configuration.
    """
    aspect_type = parzzley.sync.aspect.aspect_type_by_name(aspect_config.type_name)
    if aspect_type is None:
        raise ValueError(f"unknown aspect: {aspect_config.type_name}")
    return aspect_type(**aspect_config.arguments)


def load_logging(logger_config: "parzzley.config.Logging") -> "parzzley.sync.logger.Logging":
    """
    Return a logging for a logging configuration.

    :param logger_config: The logging configuration.
    """
    return parzzley.sync.logger.Logging(
        min_severity=(
            parzzley.sync.logger.Severity.INFO
            if logger_config.min_severity is None
            else parzzley.config.file_formats.log_severity(logger_config.min_severity)
        ),
        max_severity=(
            None
            if logger_config.max_severity is None
            else parzzley.config.file_formats.log_severity(logger_config.max_severity)
        ),
        out=(load_logger_out(_) for _ in logger_config.out),
        formatter=load_log_formatter(logger_config.formatter),
        exclude=(load_log_exclusion(_) for _ in logger_config.exclude),
    )


def load_log_formatter(log_formatter_config: "parzzley.config.Logging.Formatter") -> "parzzley.sync.logger.Formatter":
    """
    Return a log formatter for a log formatter configuration.

    :param log_formatter_config: The log formatter configuration.
    """
    log_formatter_type = parzzley.sync.logger.formatter_type_by_kind(log_formatter_config.kind)
    if log_formatter_type is None:
        raise ValueError(f"unknown log formatter kind: {log_formatter_config.kind}")
    return log_formatter_type(**log_formatter_config.arguments)


def load_logger_out(logger_out_config: "parzzley.config.Logging.Out") -> "parzzley.sync.logger.Out":
    """
    Return a logger output channel for a logger output channel configuration.

    :param logger_out_config: The logger output channel configuration.
    """
    logger_out_type = parzzley.sync.logger.out_by_kind(logger_out_config.kind)
    if logger_out_type is None:
        raise ValueError(f"unknown logger output channel kind: {logger_out_config.kind}")
    return logger_out_type(**logger_out_config.arguments)


def load_log_exclusion(log_exclusion_config: "parzzley.config.Logging.Exclude") -> "parzzley.sync.logger.Exclude":
    """
    Return a logger exclusion for a logger exclusion configuration.

    :param log_exclusion_config: The logger exclusion configuration.
    """
    return parzzley.sync.logger.Exclude((load_log_exclusion_condition(_) for _ in log_exclusion_config.conditions))


def load_log_exclusion_condition(
    log_exclusion_condition_config: "parzzley.config.Logging.Exclude.BaseCondition",
) -> "parzzley.sync.logger.Exclude.Condition":
    """
    Return a logger exclusion condition for a logger exclusion condition configuration.

    :param log_exclusion_condition_config: The logger exclusion condition configuration.
    """
    if isinstance(log_exclusion_condition_config, parzzley.config.Logging.Exclude.Condition):
        return parzzley.sync.logger.conditions.SimpleCondition(**log_exclusion_condition_config.arguments)

    if isinstance(log_exclusion_condition_config, parzzley.config.Logging.Exclude.CombinedCondition):
        return (
            parzzley.sync.logger.conditions.ConditionAllOf
            if log_exclusion_condition_config.combination == "AND"
            else parzzley.sync.logger.conditions.ConditionAnyOf
        )(conditions=(load_log_exclusion_condition(_) for _ in log_exclusion_condition_config.conditions))

    if isinstance(log_exclusion_condition_config, parzzley.config.Logging.Exclude.NegateCondition):
        return parzzley.sync.logger.conditions.ConditionNegate(
            condition=load_log_exclusion_condition(log_exclusion_condition_config.condition)
        )

    raise ValueError(f"invalid log exclusion condition configuration: {log_exclusion_condition_config}")
