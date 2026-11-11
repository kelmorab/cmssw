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

hltTriggerPathTablesTask = cms.Task(
    hltTriggerPathBitsTable
)
