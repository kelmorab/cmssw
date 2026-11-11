import FWCore.ParameterSet.Config as cms

# ---------------------------------------------------------------------------
# Trigger decisions of paths that the NanoAOD output module does not write.
#
# The NanoAOD output module writes trigger bits only for paths whose name
# starts with "HLT", "L1" or "Flag", or contains "Scouting". The decisions of
# all other paths are dropped, e.g. MC_*, AlCa_*, Dataset_*, DQM_*, Status_*
# and DST_* paths without "Scouting" in the name (in the Phase-2 menu
# HLT:@relvalRun4 of CMSSW_20_1_0_pre4: the 5 MC_* and 2 DQM_* paths).
#
# hltTriggerPathBitsTable writes them as bool branches named like the paths
# (e.g. "MC_JME"), with the same title as the NanoAOD trigger bits
# ("Trigger/flag bit (process: HLT2)"), so readers of NanoAOD trigger bits
# pick them up like the HLT_* bits. Paths that the NanoAOD output module
# writes itself are skipped (skipPathsWrittenByNanoAOD).
#
# The module reads the TriggerResults of the current process, which only
# exists after all Paths have finished. It must therefore be in a Task (it
# then runs when the NanoAOD output module, on an EndPath, asks for the
# table), never on a Path. For NANO-only jobs (HLT run in an earlier job)
# hltNanoCustomize switches the input to the TriggerResults of that job.
# ---------------------------------------------------------------------------

hltTriggerPathBitsTable = cms.EDProducer(
    "TriggerPathStatusTableProducer",
    src = cms.InputTag("TriggerResults", "", "@currentProcess"),
    # empty table name: branches are named like the paths
    name = cms.string(""),
    paths = cms.vstring("MC_*", "AlCa_*", "Dataset_*", "DQM_*", "DST_*", "Status_*"),
    skipPathsWrittenByNanoAOD = cms.bool(True),
    stripVersions = cms.bool(True),
)

# ---------------------------------------------------------------------------
# Per-filter rates: index of the last module that ran on each path.
#
# Branches PathLastModule_<path> (uint16) = edm::HLTPathStatus::index():
#  - path rejected the event: index of the module that rejected it;
#  - path accepted the event: index of the last module of the path;
#  - 65535: path not in the menu of this run.
# The module list of each path is in the ParameterSets tree of the NANO file
# (process configuration of the HLT process, parameter named like the path,
# labels in path order). An event passed module k of path P if
# PathLastModule_P > k, or if P accepted the event (then PathLastModule_P is
# the index of the last module). This gives rates after each filter, for every path and
# also for filters that save no trigger objects. The per-object flags of
# the TriggerObject table cannot give this: a filter saves the objects that
# pass its per-object cuts also when the event fails the filter.
# Most paths stop at the L1 seed filter or the prescaler, so the values
# compress well.
# ---------------------------------------------------------------------------

hltTriggerPathLastModuleTable = hltTriggerPathBitsTable.clone(
    content = cms.string("lastModuleIndex"),
    name = "PathLastModule",
    # all physics/calibration/monitoring paths, including the HLT_* paths
    # (no clash with the NanoAOD trigger bits: own table name)
    paths = ["HLT_*", "MC_*", "DST_*", "AlCa_*", "Dataset_*", "DQM_*", "Status_*"],
    skipPathsWrittenByNanoAOD = False,
)

hltTriggerPathTablesTask = cms.Task(
    hltTriggerPathBitsTable,
    hltTriggerPathLastModuleTable
)
