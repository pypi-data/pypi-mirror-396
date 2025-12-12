#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Common default sync aspects; basically combining some of the other ones together for simpler usage.
"""
import parzzley.builtin.aspects.attach_sites
import parzzley.builtin.aspects.conflicts
import parzzley.builtin.aspects.directory
import parzzley.builtin.aspects.item_type
import parzzley.builtin.aspects.main_stream
import parzzley.builtin.aspects.posix_attributes
import parzzley.builtin.aspects.remove
import parzzley.builtin.aspects.streaming
import parzzley.builtin.aspects.sync_report
import parzzley.builtin.aspects.xattrs


class DefaultBase(parzzley.sync.aspect.Aspect):
    """
    Collection of base aspects required in many setups, but not yet a complete setup.
    See e.g. :py:class:`DefaultSync` and :py:mod:`parzzley.builtin.aspects.pull_and_purge`.
    """

    def __init__(self):
        super().__init__(
            parzzley.builtin.aspects.attach_sites.AttachSites(),
            parzzley.builtin.aspects.conflicts.ApplyConflictResolution(),
            parzzley.builtin.aspects.directory.RemoveForReplacement(),
            parzzley.builtin.aspects.directory.RollbackCrashedTransfers(),
            parzzley.builtin.aspects.directory.ListDirectory(),
            parzzley.builtin.aspects.directory.MarkChangedIfItemIsDirectoryButWasNotBefore(),
            parzzley.builtin.aspects.item_type.DetermineItemTypes(),
            parzzley.builtin.aspects.main_stream.MainStreamSynchronization(),
            parzzley.builtin.aspects.posix_attributes.PosixAttributesSynchronization(),
            parzzley.builtin.aspects.streaming.GlobalStreamSupport(),
            parzzley.builtin.aspects.streaming.SkipItemIfNoUpToDateSitesAreConnected(),
            parzzley.builtin.aspects.streaming.SetItemsBookEntry(),
            parzzley.builtin.aspects.streaming.SourceStreamable(),
            parzzley.builtin.aspects.streaming.GetCookie(),
            parzzley.builtin.aspects.streaming.ComputeMasterSiteTable(),
            parzzley.builtin.aspects.streaming.UpdateTransfer(),
            parzzley.builtin.aspects.streaming.StickToOldMasterSitesOnItemRetry(),
            parzzley.builtin.aspects.sync_report.SyncReport(),
            parzzley.builtin.aspects.xattrs.XattrSynchronization(),
        )


@parzzley.sync.aspect.register_aspect
class DefaultSync(parzzley.sync.aspect.Aspect):
    """
    Nearly complete sync setup; only missing a removal strategy (see :py:mod:`parzzley.builtin.aspects.remove`).
    """

    def __init__(self):
        super().__init__(
            DefaultBase(),
            parzzley.builtin.aspects.conflicts.DetectContentConflicts(),
            parzzley.builtin.aspects.conflicts.DetectItemTypeConflicts(),
            parzzley.builtin.aspects.conflicts.TrackConflicts(),
            parzzley.builtin.aspects.conflicts.TryResolveConflictsByHint(),
            parzzley.builtin.aspects.directory.DirectoryCreation(),
            parzzley.builtin.aspects.remove.DetectRemoval(),
            parzzley.builtin.aspects.streaming.WorkingItem(),
        )
