export const mockAPICall = async () => {
  var mockData = [
    [1, "To monitor network....", ["Metric-1", "Metric-2", "Metric-3"]],
    [2, "", ["Metric-2", "Metric-3"]],
    [3, "", ["Metric-1", "Metric-3"]],
    [4, "", ["Metric-3"]],
    [5, "", ["Metric-1", "Metric-2", "Metric-3"]],
    [6, "", ["Metric-1", "Metric-2", "Metric-3"]],
  ];

  return Promise.resolve(mockData);
};
