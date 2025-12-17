const standardMetrics = require('./standard_metrics.json');
const standardDqDimensions = require('./standard_dq_dimensions.json');
const standardDataRules = require('./standard_data_rules.json');
const rootCauseFactors = require('./root_cause_factors.json');
const businessProcessMaps = require('./business_process_maps.json');

module.exports = {
  standardMetrics,
  standardDqDimensions,
  standardDataRules,
  rootCauseFactors,
  businessProcessMaps,
  physicalDataMap: require('./physical_data_map.json'),
  ontologyGraph: require('./ontology_graph.json')
};
