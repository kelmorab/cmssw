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

######################################
# Tables 
######################################

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

def hltNanoCustomize(process):

    _ignoreHLTProductsOfInputFile(process)

    if hasattr(process, "NANOAODSIMoutput"):
        # process.genJetTable.cut = "pt > 10"
        # process.genJetFlavourTable.deltaR = 0.3
        process.genParticleTable.externalVariables = cms.PSet() # remove iso as external variable from PhysicsTools/NanoAOD/python/genparticles_cff.py:37 (hopefully temporarily)
        process.genParticleTable.variables.vx = Var("vx", float, precision=10, doc="x coordinate of production vertex")
        process.genParticleTable.variables.vy = Var("vy", float, precision=10, doc="y coordinate of production vertex")
        process.genParticleTable.variables.vz = Var("vz", float, precision=16, doc="z coordinate of production vertex")
        process.NANOAODSIMoutput.outputCommands.append(
            "keep nanoaodFlatTable_*Table*_*_*"
        )
        process.NANOAODSIMoutput.SelectEvents = cms.untracked.PSet(
            SelectEvents = cms.vstring(
                [p for p in process.paths if p.startswith('HLT_') or p.startswith('MC_') or p.startswith('DST_')]
            )
        )

        # disable SelectEvents for nano_l1_hlt
        nano_l1_hlt.toModify(
            process.NANOAODSIMoutput,
            SelectEvents = cms.untracked.PSet()
        )

    return process
