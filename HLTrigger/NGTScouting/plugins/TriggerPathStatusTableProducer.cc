// TriggerPathStatusTableProducer
//
// Writes per-path information of an edm::TriggerResults into a singleton
// nanoaod::FlatTable: one entry per event, one column per selected path.
//
// Motivation
// ----------
// The NanoAOD output module turns every edm::TriggerResults in the event into
// bool branches, but only for paths whose name starts with "HLT", "L1" or
// "Flag", or contains "Scouting" (PhysicsTools/NanoAOD/plugins/
// TriggerOutputBranches.cc). The decisions of all other paths of the menu are
// dropped silently, e.g. MC_*, AlCa_*, Dataset_*, DQM_*, Status_* and DST_*
// paths without "Scouting" in their name. They are needed e.g. for rate
// estimates of the full menu (AlCa_* streams, dataset rates from Dataset_*).
// This module writes them without changing the NanoAOD output module.
//
// What is written per path ("content")
// ------------------------------------
//  - "accept" (default): the path decision, bool.
//  - "lastModuleIndex": edm::HLTPathStatus::index(), uint16: the index of the
//    last module that ran on the path. For a path that rejected the event,
//    this is the module that rejected it; for an accepted path, it is the
//    last module of the path. Together with the module list of the path,
//    which is stored in the ParameterSets tree of every NANO file (process
//    configuration, parameter named like the path, labels in path order),
//    this gives the number of events passing EACH module of the path, i.e.
//    rates after each filter, also for filters that save no trigger objects.
//    Per-object flags ("object saved by filter X", TrigObjP4FlatTableProducer)
//    cannot provide this: a filter saves the objects that pass its
//    per-object cuts also when the event fails the filter (e.g. multiplicity
//    or HT threshold not reached). Paths missing from the menu of the current
//    run get the value 65535.
//
// Branch names and titles
// -----------------------
// With an empty table name (name = ""), the branches are named exactly like
// the paths (e.g. "MC_JME") and get the same title as the trigger bits of the
// NanoAOD output module ("Trigger/flag bit (process: HLT2)"), so code that
// reads NanoAOD trigger bits can treat both alike. Version suffixes "_v<N>"
// are removed, as the NanoAOD output module does for HLT paths.
//
// Path selection
// --------------
// "paths" is a list of glob patterns ("MC_*"). Paths whose bits the NanoAOD
// output module writes itself are skipped by default
// (skipPathsWrittenByNanoAOD), since two branches with the same name cannot
// coexist in the Events tree.
//
// Scheduling
// ----------
// The TriggerResults of the CURRENT process is produced after all Paths have
// finished. A module reading it must therefore not run on a Path: put it in a
// Task, so that it runs on demand when the NanoAOD output module (EndPath)
// asks for the table.
//
// Several runs with different menus in one job
// --------------------------------------------
// The NanoAOD output module books the branches with the first table it sees,
// so the set of columns is fixed by the menu of the first event. For later
// menus, booked paths that are missing are written as false (or 65535), and
// paths that are not booked are skipped with a warning.

#include <algorithm>
#include <cstdint>
#include <memory>
#include <regex>
#include <string>
#include <utility>
#include <vector>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/Provenance/interface/ParameterSetID.h"
#include "DataFormats/Provenance/interface/Provenance.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/allowedValues.h"
#include "FWCore/Utilities/interface/RegexMatch.h"

class TriggerPathStatusTableProducer : public edm::stream::EDProducer<> {
public:
  explicit TriggerPathStatusTableProducer(const edm::ParameterSet&);
  static void fillDescriptions(edm::ConfigurationDescriptions&);

  enum class Content { accept, lastModuleIndex };
  // value of a lastModuleIndex column for a path that is not in the current menu
  static constexpr uint16_t kPathNotInMenu = 65535;

private:
  void produce(edm::Event&, const edm::EventSetup&) override;

  // (Re)compute which path of the current menu fills which column.
  void updateColumns(const edm::TriggerNames&);

  // Same name filter as the NanoAOD output module (TriggerOutputBranches.cc).
  static bool isWrittenByNanoAOD(const std::string& pathName);
  // "MC_JME_v12" -> "MC_JME"
  static std::string stripVersion(const std::string& pathName);

  const edm::EDGetTokenT<edm::TriggerResults> resultsToken_;
  const std::string tableName_;
  const std::vector<std::string> pathPatterns_;
  const bool skipPathsWrittenByNanoAOD_;
  const bool stripVersions_;
  const Content content_;

  struct Column {
    std::string name;    // column (= branch) name
    int pathIndex = -1;  // index of the path in the current TriggerResults, -1 if not in the current menu
  };
  std::vector<Column> columns_;
  bool columnsBooked_ = false;
  edm::ParameterSetID menuID_;
};

TriggerPathStatusTableProducer::TriggerPathStatusTableProducer(const edm::ParameterSet& params)
    : resultsToken_(consumes<edm::TriggerResults>(params.getParameter<edm::InputTag>("src"))),
      tableName_(params.getParameter<std::string>("name")),
      pathPatterns_(params.getParameter<std::vector<std::string>>("paths")),
      skipPathsWrittenByNanoAOD_(params.getParameter<bool>("skipPathsWrittenByNanoAOD")),
      stripVersions_(params.getParameter<bool>("stripVersions")),
      content_(params.getParameter<std::string>("content") == "lastModuleIndex" ? Content::lastModuleIndex
                                                                                : Content::accept) {
  produces<nanoaod::FlatTable>();
}

bool TriggerPathStatusTableProducer::isWrittenByNanoAOD(const std::string& pathName) {
  return pathName.compare(0, 3, "HLT") == 0 || pathName.compare(0, 2, "L1") == 0 ||
         pathName.compare(0, 4, "Flag") == 0 || pathName.find("Scouting") != std::string::npos;
}

std::string TriggerPathStatusTableProducer::stripVersion(const std::string& pathName) {
  static const std::regex versionSuffix("_v[0-9]+$");
  return std::regex_replace(pathName, versionSuffix, "");
}

void TriggerPathStatusTableProducer::updateColumns(const edm::TriggerNames& names) {
  const auto& allNames = names.triggerNames();

  // Paths of this menu matching any pattern, as (path index, column name).
  std::vector<std::pair<unsigned int, std::string>> selected;
  std::vector<bool> taken(allNames.size(), false);
  for (const auto& pattern : pathPatterns_) {
    for (const auto& match : edm::regexMatch(allNames, pattern)) {
      const unsigned int index = match - allNames.begin();
      if (taken[index])
        continue;
      taken[index] = true;
      if (skipPathsWrittenByNanoAOD_ && isWrittenByNanoAOD(*match))
        continue;
      selected.emplace_back(index, stripVersions_ ? stripVersion(*match) : *match);
    }
  }
  std::sort(selected.begin(), selected.end());  // menu order

  if (!columnsBooked_) {
    // First menu of this stream: defines the columns.
    for (const auto& [index, name] : selected)
      columns_.push_back({name, static_cast<int>(index)});
    columnsBooked_ = true;
    return;
  }

  // Later menu (new run): keep the booked columns, map them to the new path indices.
  for (auto& column : columns_)
    column.pathIndex = -1;
  for (const auto& [index, name] : selected) {
    auto found = std::find_if(columns_.begin(), columns_.end(), [&](const Column& c) { return c.name == name; });
    if (found != columns_.end()) {
      found->pathIndex = index;
    } else {
      edm::LogWarning("TriggerPathStatusTableProducer")
          << "Path " << name << " is not in the menu of the first event of this job; it is not written.";
    }
  }
}

void TriggerPathStatusTableProducer::produce(edm::Event& event, const edm::EventSetup&) {
  const auto resultsHandle = event.getHandle(resultsToken_);
  const edm::TriggerResults& results = *resultsHandle;
  const edm::TriggerNames& names = event.triggerNames(results);

  // The menu can only change between runs. TriggerResults that carry their
  // path names themselves (no valid ParameterSetID) are re-checked every event.
  if (!columnsBooked_ || !names.parameterSetID().isValid() || names.parameterSetID() != menuID_) {
    updateColumns(names);
    menuID_ = names.parameterSetID();
  }

  const std::string& process = resultsHandle.provenance()->processName();
  auto table = std::make_unique<nanoaod::FlatTable>(1, tableName_, true);

  if (content_ == Content::accept) {
    // Same title as the trigger bits written by the NanoAOD output module.
    const std::string doc = "Trigger/flag bit (process: " + process + ")";
    for (const auto& column : columns_) {
      const bool accept = column.pathIndex >= 0 && results.accept(column.pathIndex);
      table->addColumnValue<bool>(column.name, accept, doc);
    }
  } else {
    const std::string doc =
        "index of the last module run on this path (edm::HLTPathStatus::index(), process: " + process +
        "): the module that rejected the event if the path failed, the last module of the path "
        "if it accepted; module list of the path in the ParameterSets tree; " +
        std::to_string(kPathNotInMenu) + " = path not in the menu of this run";
    for (const auto& column : columns_) {
      const uint16_t index =
          column.pathIndex >= 0 ? static_cast<uint16_t>(results.index(column.pathIndex)) : kPathNotInMenu;
      table->addColumnValue<uint16_t>(column.name, index, doc);
    }
  }
  event.put(std::move(table));
}

void TriggerPathStatusTableProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.setComment(
      "Writes the decisions (or the index of the last module run) of selected paths of an edm::TriggerResults into "
      "a singleton nanoaod::FlatTable, e.g. for paths whose bits the NanoAOD output module does not write (MC_*, "
      "AlCa_*, Dataset_*, ...) or for per-filter rates. When reading the TriggerResults of the current process, "
      "the module must be in a Task, not on a Path.");
  desc.add<edm::InputTag>("src", edm::InputTag("TriggerResults", "", "@currentProcess"))
      ->setComment("TriggerResults to read");
  desc.add<std::string>("name", "")
      ->setComment(
          "Table name. Empty: the branches are named like the paths, as the trigger bits of the NanoAOD output "
          "module");
  desc.add<std::vector<std::string>>("paths", {"MC_*", "AlCa_*", "Dataset_*", "DQM_*", "DST_*", "Status_*"})
      ->setComment("Glob patterns of the paths to write");
  desc.add<bool>("skipPathsWrittenByNanoAOD", true)
      ->setComment(
          "Skip paths whose bits the NanoAOD output module writes itself (name starts with HLT, L1 or Flag, or "
          "contains Scouting), to avoid two branches with the same name");
  desc.add<bool>("stripVersions", true)->setComment("Remove the version suffix _v<N> from the path names");
  desc.ifValue(edm::ParameterDescription<std::string>("content", "accept", true),
               edm::allowedValues<std::string>("accept", "lastModuleIndex"))
      ->setComment(
          "accept: path decision (bool). lastModuleIndex: edm::HLTPathStatus::index() (uint16), the index of the "
          "last module run on the path, " +
          std::to_string(kPathNotInMenu) + " if the path is not in the menu of the current run");
  descriptions.addWithDefaultLabel(desc);
}

DEFINE_FWK_MODULE(TriggerPathStatusTableProducer);
