import FWCore.ParameterSet.Config as cms

from PhysicsTools.JetMCAlgos.AK4GenJetFlavourInfos_cfi import *
from PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi import *
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.genparticles_cff import *
from PhysicsTools.NanoAOD.genVertex_cff import *
from PhysicsTools.NanoAOD.jetMC_cff import *
from PhysicsTools.NanoAOD.taus_cff import *
from PhysicsTools.PatAlgos.slimming.genParticles_cff import *
from PhysicsTools.PatAlgos.slimming.packedGenParticles_cfi import *
from PhysicsTools.PatAlgos.slimming.prunedGenParticles_cfi import *
from PhysicsTools.PatAlgos.slimming.slimmedGenJetsFlavourInfos_cfi import *
from PhysicsTools.PatAlgos.slimming.slimmedGenJets_cfi   import *
from RecoJets.Configuration.GenJetParticles_cff import *
from RecoJets.Configuration.RecoGenJets_cff import *
from HLTrigger.NGTScouting.hltVertices_cfi import *
from HLTrigger.NGTScouting.hltEGammaPacker_cfi import *
from HLTrigger.NGTScouting.hltPhotons_cfi import *
from HLTrigger.NGTScouting.hltElectrons_cfi import *
from HLTrigger.NGTScouting.hltMuons_cfi import *
from HLTrigger.NGTScouting.hltTracks_cfi import *
from HLTrigger.NGTScouting.hltGsfTracks_cfi import *
from HLTrigger.NGTScouting.hltJets_cfi import *
from HLTrigger.NGTScouting.hltTaus_cfi import *
from HLTrigger.NGTScouting.hltTracksters_cfi import *
from HLTrigger.NGTScouting.hltTICLCandidates_cfi import *
from HLTrigger.NGTScouting.hltTICLSuperClusters_cfi import *
from HLTrigger.NGTScouting.hltLayerClusters_cfi import * 
from HLTrigger.NGTScouting.hltSums_cfi import *
from HLTrigger.NGTScouting.hltTriggerObjects_cff import *
from HLTrigger.NGTScouting.hltTriggerAcceptFilter_cfi import hltTriggerAcceptFilter,dstTriggerAcceptFilter
from DPGAnalysis.Phase2L1TNanoAOD.l1tPh2GTtables_cff import l1tP2GTTrigConvert

######################################
# Tables
######################################

# Phase-2 L1 Global Trigger (GT) algorithm decisions as trigger bits.
#
# The GT algorithms of the menu (pSingleTkMuon22, ...) are cms.Paths of the
# L1P2GT step, but the NanoAOD output module only writes trigger bits whose
# name starts with "HLT", "L1" or "Flag" (or contains "Scouting"), so their
# decisions are not in the HLT NANO by default. P2GTTriggerResultsConverter
# (DPGAnalysis/Phase2L1TNanoAOD) converts the GT algo block into an
# edm::TriggerResults with names "L1_<algo>_<decision>", which the NanoAOD
# output module then writes as bool branches, e.g. L1_pSingleTkMuon22_final.
# Two decisions are stored:
#  - "final": after BX mask and prescale. This is what the HLT sees
#    (hltL1GTAcceptFilter uses decision = "final"). The module is the same
#    one as in the Phase-2 L1 DPG NANO (NANO:@Phase2L1DPG), so combining both
#    flavours (NANO:@Phase2HLT+@Phase2L1DPG) gives each bit once.
#  - "beforePrescale": after BX mask, before prescale. Needed to apply other
#    prescale columns later, e.g. in rate estimates. The GT emulator
#    prescales default to 1, so both decisions agree unless the emulated menu
#    sets prescales.
# NB: the NanoAOD output module cuts L1/HLT names at the last "_v" (version
# suffix). GT algorithm names containing "_v" would be truncated.
l1tP2GTTrigConvertBeforePrescale = l1tP2GTTrigConvert.clone(
    decision = "beforePrescale"
)
NanoL1GTBits = cms.Sequence(
    l1tP2GTTrigConvert
    + l1tP2GTTrigConvertBeforePrescale
)

# MC event weights, weight sums and pileup information.
#
# Needed to normalise MC, e.g. for trigger rates:
#  - hltGenWeightsTable: per event "genWeight" (and PS/LHE weights if
#    available), and in the Runs tree the sums over ALL processed events
#    (genEventCount, genEventSumw, genEventSumw2, ...). The sums are
#    accumulated in produce(), so these modules must be scheduled on the NANO
#    path, before any filter; see hltNanoCustomize. Then the sums count every
#    processed event, also those not written because of the output event
#    selection (NANOAODSIMoutput.SelectEvents);
#  - hltGeneratorTable: Generator_weight, Generator_binvar (pT-hat for binned
#    QCD samples), PDF info;
#  - hltPileupTable: Pileup_nTrueInt, Pileup_nPU, Pileup_pthatmax, ... read
#    from the GEN-SIM-DIGI-RAW product addPileupInfo (the standard NANO reads
#    the MINIAOD copy slimmedAddPileupInfo). The PU density variables need
#    offline primary vertices and are switched off.
# These modules use their own labels (not genWeightsTable/genTable/puTable),
# so that they do not clash with the standard NANO modules, which other
# flavours (e.g. NANO:@Phase2L1DPG) load into the same process.
from PhysicsTools.NanoAOD.genWeightsTable_cfi import genWeightsTable as _genWeightsTable
from PhysicsTools.NanoAOD.globals_cff import genTable as _genTable, puTable as _puTable
hltGenWeightsTable = _genWeightsTable.clone()
hltGeneratorTable = _genTable.clone()
hltPileupTable = _puTable.clone(
    src = "addPileupInfo",
    savePUDensityVars = False
)
NanoMCWeightTables = cms.Sequence(
    hltGenWeightsTable
    + hltGeneratorTable
    + hltPileupTable
)

# Produce and store gen particles and gen jets
NanoGenTables = cms.Sequence(
    prunedGenParticlesWithStatusOne
    + prunedGenParticles
    + finalGenParticles
    + genParticleTable
    + genVertexTable
    + genParticlesForJetsNoNu
    + ak4GenJetsNoNu
    + selectedHadronsAndPartonsForGenJetsFlavourInfos
    + packedGenParticles
    + slimmedGenJets
    + ak4GenJetFlavourInfos
    + slimmedGenJetsFlavourInfos
    + genJetTable
    + genJetFlavourTable
    + tauGenJetsForNano
    + tauGenJetsSelectorAllHadronsForNano
    + genVisTaus
    + genVisTauTable
)

# Store hlt objects for NGT scouting
NanoHltTables = cms.Sequence(
    hltTriggerObjP4Table
    + hltVertexTable
    + hltPixelVertexTable
    + hltGeneralTrackTable
    + hltGeneralTrackExtTable
    + hltGsfTracksL1SeededTable
    + hltGsfTracksUnseededTable
    + hltEgammaPacker
    + hltPhotonTable
    + hltElectronTable
    + hltPhase2L3MuonIdTracks
    + hltMuonTable
    + hltPFCandidateTable
    + hltJetTable
    + hltTauTable
    + hltTauExtTable
    + METTable
    + HTTable
)

# Store HGCal lower-level objects
NanoHGCalTables = cms.Sequence(
    hltTrackstersTableSequence
    + hltTiclCandidateTable
    + hltTiclCandidateExtraTable
    + hltTiclSuperClustersTable
)

# Store PixelTracks objects
NanoPixelTables = cms.Sequence(
    pixelTrackAssoc
    + hltPixelTrackTable
    + hltPixelTrackExtTable
    + hltPixelTrackRecHitsTable
)

# Store variables and associators for validation purposes
NanoValTables = cms.Sequence(
    hltTiclAssociationsTableSequence
    + hltSimTracksterSequence
    + hltSimTiclCandidateTable
    + hltSimTiclCandidateExtraTable
    + hltLayerClustersTableSequence
    + hltTrackingParticleRecoTrackAssociationTable
    + hltRecoTrackTrackingParticleAssociationTable
)

######################################
# Sequences for Nano flavours
######################################

# NGT Scouting Nano flavour (NANO:@NGTScouting)
dstNanoFlavour = cms.Sequence(
    NanoHltTables.copyAndExclude([hltGsfTracksL1SeededTable])
)

# NGT Scouting Nano flavour with MC/HGCal info (NANO:@NGTScoutingVal)
dstValidationNanoFlavour = cms.Sequence(
    NanoGenTables
    + dstTriggerAcceptFilter
    + NanoHltTables
    + NanoPixelTables
    + NanoHGCalTables
    + NanoValTables
)

# Phase-2 HLT Nano flavour (NANO:@Phase2HLT)
hltNanoFlavour = cms.Sequence(
    NanoHltTables
    + NanoL1GTBits
)

# Phase-2 HLT Nano flavour with MC/HGCal info (NANO:@Phase2HLTVal)
hltValidationNanoFlavour = cms.Sequence(
    NanoGenTables
    + NanoHltTables
    + NanoPixelTables
    + NanoHGCalTables
    + NanoValTables
)

# Phase-2 HLT Nano flavour for pixel tracking validation / optimization
hltPixelOnlyNanoFlavour = cms.Sequence(
    NanoGenTables
    + NanoPixelTables
)

from Configuration.ProcessModifiers.nano_l1_hlt_cff import nano_l1_hlt
nano_l1_hlt.toReplaceWith(dstValidationNanoFlavour, dstValidationNanoFlavour.copyAndExclude([dstTriggerAcceptFilter]))

######################################
# Customization
######################################

def _jobRunsHLT(process):
    """True if the HLT menu runs in this job (HLT re-run and NANO in one job),
    False if only the NANO step runs on the output of an earlier HLT job."""
    return hasattr(process, "hltTriggerSummaryAOD")

def _ignoreHLTProductsOfInputFile(process):
    """If the HLT is re-run in this job, do not read the HLT products of the input file.

    Use case: re-running L1+HLT on GEN-SIM-DIGI-RAW that already contains an
    HLT step (e.g. the Phase-2 RelVals, whose HLT ran in process "HLT"), with
    cmsDriver --processName HLT2 and NANO in the same job. Without this, the
    products of the OLD HLT step leak into the output:
      - the NanoAOD output module writes every edm::TriggerResults in the
        event, so the old HLT decisions appear next to the new ones as
        <path>_p<process> branches (e.g. HLT_IsoMu24_FromL1TkMuon_pHLT) and
        tools must know which process to use;
      - the Phase-2 menu runs hltTriggerSummaryAOD with processName = "*", so
        the TriggerEvent of the re-run also collects the filter objects of the
        old HLT step (log message of TriggerSummaryProducerAOD:
        "Mismatch in number of filter tags: N!=M").
    This is the same as running cmsDriver with
      --inputCommands 'keep *, drop *_hlt*_*_HLT, drop triggerTriggerFilterObjectWithRefs_*_*_HLT, drop edmTriggerResults_*_*_HLT'
    (see test/testNanohltDQM.sh), but independent of the process name of the
    old HLT step. inputCommands only act on products read from the input
    file, so the products of the current process are not affected.

    To keep the old decisions (e.g. for comparisons), override
    process.source.inputCommands via cmsDriver --customise_commands, which
    run after this customisation.
    """
    if not _jobRunsHLT(process):
        # NANO-only job: the input file holds the HLT results we want to write.
        return
    if not hasattr(process, "source") or process.source.type_() != "PoolSource":
        return
    commands = list(process.source.inputCommands) if hasattr(process.source, "inputCommands") else ["keep *"]
    commands += [
        # HLT reconstruction products and hltTriggerSummaryAOD of earlier HLT steps
        "drop *_hlt*_*_*",
        # filter objects (incl. the l1t* GT algo filters) of earlier HLT/L1 steps
        "drop triggerTriggerFilterObjectWithRefs_*_*_*",
        # path decisions of earlier processes (HLT, SIM, ...)
        "drop edmTriggerResults_*_*_*",
    ]
    process.source.inputCommands = cms.untracked.vstring(commands)

def _l1AcceptPaths(process):
    """Path(s) for selecting events in which any Phase-2 L1 GT algorithm fired, BEFORE prescale.

    Adds (once) the path hltNanoL1GTAcceptPath with an L1GTAcceptFilter
    (decision = "beforePrescale"), the module the HLT paths use for their L1
    seeding (there with decision = "final"). It accepts an event if any
    physics algorithm of the GT menu fired (and no veto algorithm), so every
    event that some L1 prescale column could accept is selected.
    The single GT algorithm paths (pSingleTkMuon22, ...) cannot be used
    directly: an algorithm can combine several paths (e.g.
    "pPuppiHT400 and pQuadJet70_55_40_40"), while SelectEvents can only OR
    path decisions.
    The path name does not start with "HLT", "L1" or "Flag", so the NanoAOD
    output module does not write it as a trigger bit.
    Returns [] if the GT does not run in this job.
    """
    if not hasattr(process, "l1tGTAlgoBlockProducer"):
        return []
    if not hasattr(process, "hltNanoL1GTAcceptPath"):
        from L1Trigger.Phase2L1GT.l1GTAcceptFilter_cff import l1tGTAcceptFilter
        process.hltNanoL1GTAcceptFilter = l1tGTAcceptFilter.clone(decision = cms.string("beforePrescale"))
        process.hltNanoL1GTAcceptPath = cms.Path(process.hltNanoL1GTAcceptFilter)
        if process.schedule is not None:
            # insert before the first EndPath, i.e. among the other Paths
            endPaths = [i for i, p in enumerate(process.schedule) if isinstance(p, cms.EndPath)]
            process.schedule.insert(endPaths[0] if endPaths else len(process.schedule),
                                    process.hltNanoL1GTAcceptPath)
    return ["hltNanoL1GTAcceptPath"]

def _usesPhase2HLTFlavour(process):
    """True if the NANO:@Phase2HLT flavour (hltNanoFlavour) runs in this job.

    hltNanoCustomize is shared by all flavours of this file (NGTScouting,
    Phase2HLTVal, ...). Changes meant for NANO:@Phase2HLT only check this.
    l1tP2GTTrigConvertBeforePrescale is only part of hltNanoFlavour.
    """
    return any("l1tP2GTTrigConvertBeforePrescale" in path.moduleNames() for path in process.paths.values())

def _nanoOutputModules(process):
    return [getattr(process, label) for label in ("NANOAODSIMoutput", "NANOAODoutput") if hasattr(process, label)]

def _hasEventSelection(output):
    """True if an event selection (non-empty SelectEvents) is configured for the output module."""
    return (hasattr(output, "SelectEvents") and hasattr(output.SelectEvents, "SelectEvents")
            and len(output.SelectEvents.SelectEvents) > 0)

def hltNanoSelectTriggeredEvents(process):
    """Opt-in event selection: write only events that fire at least one L1 seed or HLT path.

    Meant for trigger-rate ntuples, mainly on MinBias / NuGun samples, where
    only a few percent of the events fire any L1 GT algorithm. The other
    events contribute to no L1 or HLT rate, so they need not be written.
    Rates are then normalised with the number of PROCESSED events, from the
    Runs tree (genEventCount / genEventSumw of hltGenWeightsTable, which counts
    all processed events), not with the number of entries of the Events tree.

    Kept are the events that fire any of:
      - a Phase-2 L1 GT algorithm, decision BEFORE prescale (after BX mask),
        so that every event that some prescale column could accept is kept
        (path hltNanoL1GTAcceptPath, see _l1AcceptPaths);
      - an HLT_*, DST_* or AlCa_* path.
    MC_* and DQM_* paths are not used: in the Phase-2 menu MC_JME, MC_BTV and
    MC_TRK have no filter and accept every event.
    NB: for a menu with a seed that fires on (almost) every event, e.g. a
    ZeroBias-like seed, this keeps (almost) every event.

    Not suited for efficiency or turn-on studies, which need the events that
    fail the triggers as well.

    Usage: add to the cmsDriver command
      --customise HLTrigger/NGTScouting/HLTNanoProducer_cff.hltNanoSelectTriggeredEvents
    cmsDriver applies --customise functions BEFORE the customisation of the
    NANO flavour (hltNanoCustomize); hltNanoCustomize keeps an event selection
    that is already configured, also with --procModifiers nano_l1_hlt.
    """
    paths = [p for p in process.paths if p.startswith(("HLT_", "DST_", "AlCa_"))] + _l1AcceptPaths(process)
    if not paths:
        raise RuntimeError(
            "hltNanoSelectTriggeredEvents: neither L1 GT algorithms nor HLT paths run in this job, "
            "so there is nothing to select on. Run L1P2GT and HLT in the same job as the NANO step.")
    for output in _nanoOutputModules(process):
        output.SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring(paths))
    return process

def hltNanoCustomize(process):

    _ignoreHLTProductsOfInputFile(process)

    if hasattr(process, "NANOAODSIMoutput"):
        # MC weights, weight sums and pileup for the Phase-2 HLT NANO
        # (NANO:@Phase2HLT). Inserted FIRST into the scheduled sequence, so
        # that they run for every event (see NanoMCWeightTables above).
        # MC only, since they need the generator products.
        if hasattr(process, "hltNanoFlavour"):
            process.hltNanoFlavour.insert(0, process.NanoMCWeightTables)

        # process.genJetTable.cut = "pt > 10"
        # process.genJetFlavourTable.deltaR = 0.3
        process.genParticleTable.externalVariables = cms.PSet() # remove iso as external variable from PhysicsTools/NanoAOD/python/genparticles_cff.py:37 (hopefully temporarily)
        process.genParticleTable.variables.vx = Var("vx", float, precision=10, doc="x coordinate of production vertex")
        process.genParticleTable.variables.vy = Var("vy", float, precision=10, doc="y coordinate of production vertex")
        process.genParticleTable.variables.vz = Var("vz", float, precision=16, doc="z coordinate of production vertex")
        process.NANOAODSIMoutput.outputCommands.append(
            "keep nanoaodFlatTable_*Table*_*_*"
        )
        # Default event selection: events that fire any HLT_/MC_/DST_ path,
        # and, for NANO:@Phase2HLT, also events in which any Phase-2 L1 GT
        # algorithm fired (decision before prescale, see _l1AcceptPaths), so
        # that events that only fire an L1 seed are not lost (L1 rates,
        # L1-only studies). The other flavours keep their selection as before.
        # NB: in the Phase-2 menu MC_JME, MC_BTV and MC_TRK have no filter,
        # so in practice ALL events are written. For rate ntuples, see the opt-in
        # hltNanoSelectTriggeredEvents.
        # A selection configured before this customisation (e.g. by
        # hltNanoSelectTriggeredEvents given with --customise) is kept.
        # With the process modifier nano_l1_hlt there is no default selection
        # (all events are written), as before.
        def _setDefaultEventSelection(process):
            process.NANOAODSIMoutput.SelectEvents = cms.untracked.PSet(
                SelectEvents = cms.vstring(
                    [p for p in process.paths if p.startswith('HLT_') or p.startswith('MC_') or p.startswith('DST_')]
                    + (_l1AcceptPaths(process) if _usesPhase2HLTFlavour(process) else [])
                )
            )
        if not _hasEventSelection(process.NANOAODSIMoutput):
            (~nano_l1_hlt).toModify(process, _setDefaultEventSelection)

    return process
