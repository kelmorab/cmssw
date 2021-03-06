#ifndef DQM_L1TMonitor_L1TStage2uGMT_h
#define DQM_L1TMonitor_L1TStage2uGMT_h


#include "DataFormats/L1Trigger/interface/Muon.h"
#include "DataFormats/L1TMuon/interface/RegionalMuonCand.h"
#include "L1Trigger/L1TMuon/interface/MicroGMTConfiguration.h"

#include "DQMServices/Core/interface/DQMEDAnalyzer.h"
#include "DQMServices/Core/interface/MonitorElement.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"


class L1TStage2uGMT : public DQMEDAnalyzer {

 public:

  L1TStage2uGMT(const edm::ParameterSet& ps);
  virtual ~L1TStage2uGMT();
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

 protected:

  virtual void dqmBeginRun(const edm::Run&, const edm::EventSetup&) override;
  virtual void beginLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&) override;
  virtual void bookHistograms(DQMStore::IBooker&, const edm::Run&, const edm::EventSetup&) override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;

 private:  

  edm::EDGetTokenT<l1t::RegionalMuonCandBxCollection> ugmtBMTFToken;
  edm::EDGetTokenT<l1t::RegionalMuonCandBxCollection> ugmtOMTFToken;
  edm::EDGetTokenT<l1t::RegionalMuonCandBxCollection> ugmtEMTFToken;
  edm::EDGetTokenT<l1t::MuonBxCollection> ugmtMuonToken;
  std::string monitorDir;
  bool emul;
  bool verbose;

  MonitorElement* ugmtBMTFBX;
  MonitorElement* ugmtBMTFnMuons;
  MonitorElement* ugmtBMTFhwPt;
  MonitorElement* ugmtBMTFhwEta;
  MonitorElement* ugmtBMTFhwPhi;
  MonitorElement* ugmtBMTFglbPhi;
  MonitorElement* ugmtBMTFProcvshwPhi;
  MonitorElement* ugmtBMTFhwSign;
  MonitorElement* ugmtBMTFhwSignValid;
  MonitorElement* ugmtBMTFhwQual;
  MonitorElement* ugmtBMTFlink;

  MonitorElement* ugmtOMTFBX;
  MonitorElement* ugmtOMTFnMuons;
  MonitorElement* ugmtOMTFhwPt;
  MonitorElement* ugmtOMTFhwEta;
  MonitorElement* ugmtOMTFhwPhiPos;
  MonitorElement* ugmtOMTFhwPhiNeg;
  MonitorElement* ugmtOMTFglbPhiPos;
  MonitorElement* ugmtOMTFglbPhiNeg;
  MonitorElement* ugmtOMTFProcvshwPhiPos;
  MonitorElement* ugmtOMTFProcvshwPhiNeg;
  MonitorElement* ugmtOMTFhwSign;
  MonitorElement* ugmtOMTFhwSignValid;
  MonitorElement* ugmtOMTFhwQual;
  MonitorElement* ugmtOMTFlink;

  MonitorElement* ugmtEMTFBX;
  MonitorElement* ugmtEMTFnMuons;
  MonitorElement* ugmtEMTFhwPt;
  MonitorElement* ugmtEMTFhwEta;
  MonitorElement* ugmtEMTFhwPhiPos;
  MonitorElement* ugmtEMTFhwPhiNeg;
  MonitorElement* ugmtEMTFglbPhiPos;
  MonitorElement* ugmtEMTFglbPhiNeg;
  MonitorElement* ugmtEMTFProcvshwPhiPos;
  MonitorElement* ugmtEMTFProcvshwPhiNeg;
  MonitorElement* ugmtEMTFhwSign;
  MonitorElement* ugmtEMTFhwSignValid;
  MonitorElement* ugmtEMTFhwQual;
  MonitorElement* ugmtEMTFlink;

  MonitorElement* ugmtBMTFBXvsProcessor;
  MonitorElement* ugmtOMTFBXvsProcessor;
  MonitorElement* ugmtEMTFBXvsProcessor;
  MonitorElement* ugmtBXvsLink;

  MonitorElement* ugmtMuonBX;
  MonitorElement* ugmtnMuons;
  MonitorElement* ugmtMuonIndex;
  MonitorElement* ugmtMuonhwPt;
  MonitorElement* ugmtMuonhwEta;
  MonitorElement* ugmtMuonhwPhi;
  MonitorElement* ugmtMuonhwEtaAtVtx;
  MonitorElement* ugmtMuonhwPhiAtVtx;
  MonitorElement* ugmtMuonhwCharge;
  MonitorElement* ugmtMuonhwChargeValid;
  MonitorElement* ugmtMuonhwQual;
  MonitorElement* ugmtMuonhwIso;

  MonitorElement* ugmtMuonPt;
  MonitorElement* ugmtMuonEta;
  MonitorElement* ugmtMuonPhi;
  MonitorElement* ugmtMuonEtaAtVtx;
  MonitorElement* ugmtMuonPhiAtVtx;
  MonitorElement* ugmtMuonCharge;

  MonitorElement* ugmtMuonPhiBmtf;
  MonitorElement* ugmtMuonPhiOmtf;
  MonitorElement* ugmtMuonPhiEmtf;
  MonitorElement* ugmtMuonPhiAtVtxBmtf;
  MonitorElement* ugmtMuonPhiAtVtxOmtf;
  MonitorElement* ugmtMuonPhiAtVtxEmtf;

  MonitorElement* ugmtMuonPtvsEta;
  MonitorElement* ugmtMuonPtvsPhi;
  MonitorElement* ugmtMuonPhivsEta;
  MonitorElement* ugmtMuonPtvsEtaAtVtx;
  MonitorElement* ugmtMuonPtvsPhiAtVtx;
  MonitorElement* ugmtMuonPhiAtVtxvsEtaAtVtx;

  MonitorElement* ugmtMuonBXvsLink;
  MonitorElement* ugmtMuonBXvshwPt;
  MonitorElement* ugmtMuonBXvshwEta;
  MonitorElement* ugmtMuonBXvshwPhi;
  MonitorElement* ugmtMuonBXvshwEtaAtVtx;
  MonitorElement* ugmtMuonBXvshwPhiAtVtx;
  MonitorElement* ugmtMuonBXvshwCharge;
  MonitorElement* ugmtMuonBXvshwChargeValid;
  MonitorElement* ugmtMuonBXvshwQual;
  MonitorElement* ugmtMuonBXvshwIso;
};

#endif
