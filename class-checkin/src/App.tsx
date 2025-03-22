import { useState, useEffect } from "react";
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import TimeAgo from "react-time-ago";
import JavascriptTimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";

// Initialize the time-ago library with English locale
JavascriptTimeAgo.addDefaultLocale(en);

// Time filter options
const TIME_FILTERS = {
  ALL: "All Records",
  MINUTES_30: "Last 30 Minutes",
  HOUR_1: "Last 1 Hour",
  HOURS_24: "Last 24 Hours",
  DAYS_7: "Last 7 Days",
};

export default function App() {
  const [imageKey, setImageKey] = useState(0);
  const [timeFilter, setTimeFilter] = useState(TIME_FILTERS.ALL);
  const checkins = useQuery(api.checkins.retrieve, {});

  // Refresh image every second
  useEffect(() => {
    const intervalId = setInterval(() => {
      setImageKey(prevKey => prevKey + 1);
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  // Filter checkins based on selected time range
  const filteredCheckins = () => {
    if (!checkins) return [];
    if (timeFilter === TIME_FILTERS.ALL) return checkins;

    const now = Math.floor(Date.now() / 1000); // Current time in seconds
    let timeThreshold;

    switch (timeFilter) {
      case TIME_FILTERS.MINUTES_30:
        timeThreshold = now - 30 * 60; // 30 minutes in seconds
        break;
      case TIME_FILTERS.HOUR_1:
        timeThreshold = now - 60 * 60; // 1 hour in seconds
        break;
      case TIME_FILTERS.HOURS_24:
        timeThreshold = now - 24 * 60 * 60; // 24 hours in seconds
        break;
      case TIME_FILTERS.DAYS_7:
        timeThreshold = now - 7 * 24 * 60 * 60; // 7 days in seconds
        break;
      default:
        return checkins;
    }

    return checkins.filter(checkin => checkin.timestamp >= timeThreshold);
  };

  // Function to export checkin records as CSV
  const exportToCSV = () => {
    if (!checkins || checkins.length === 0) return;

    // Define CSV headers
    const headers = ["Name", "Email", "Date", "Time", "Timestamp"];

    // Format checkin data for CSV
    const csvData = checkins.map(checkin => {
      const date = new Date(checkin.timestamp * 1000);
      return [
        checkin.name,
        checkin.email,
        date.toLocaleDateString(),
        date.toLocaleTimeString(),
        checkin.timestamp,
      ];
    });

    // Combine headers and data
    const csvContent = [headers.join(","), ...csvData.map(row => row.join(","))].join("\n");

    // Create download link
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `checkin-records-${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen p-4 gap-6 bg-gray-50">
      {/* Check-in data panel */}
      <div className="flex-1 bg-white rounded-xl p-4 shadow-sm overflow-hidden md:max-h-[calc(100vh-32px)]">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Check-in Records</h2>
          <button
            onClick={exportToCSV}
            disabled={!checkins || checkins.length === 0}
            className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed text-sm flex items-center"
          >
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Export CSV
          </button>
        </div>

        {/* Time filter */}
        <div className="mb-4">
          <div className="flex items-center space-x-2">
            <label htmlFor="time-filter" className="text-sm font-medium text-gray-700">
              Time Range:
            </label>
            <select
              id="time-filter"
              value={timeFilter}
              onChange={e => setTimeFilter(e.target.value)}
              className="block py-1.5 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              {Object.values(TIME_FILTERS).map(filter => (
                <option key={filter} value={filter}>
                  {filter}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Scrollable container */}
        <div className="overflow-y-auto max-h-[calc(100vh-180px)] pr-2">
          {checkins ? (
            filteredCheckins().length > 0 ? (
              <div className="space-y-4">
                {[...filteredCheckins()].reverse().map((checkin, index) => (
                  <div
                    key={checkin._id}
                    className={`p-5 rounded-lg ${index === 0 ? "bg-blue-50 border-blue-200" : "bg-gray-50 border-gray-100"} border hover:shadow-md transition-all duration-200`}
                  >
                    <div className="flex justify-between items-start">
                      <p className="font-bold text-gray-900 text-2xl">{checkin.name}</p>
                      <div className="flex items-center text-base font-medium text-gray-700">
                        <svg
                          className="w-5 h-5 mr-2 text-gray-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <TimeAgo date={new Date(checkin.timestamp * 1000)} />
                      </div>
                    </div>
                    <div className="flex items-center text-lg text-gray-700 mt-3">
                      <svg
                        className="w-5 h-5 mr-2 text-gray-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                        />
                      </svg>
                      {checkin.email}
                    </div>
                    <div className="flex justify-between items-center mt-4">
                      <div className="flex items-center text-base font-medium text-gray-700">
                        <svg
                          className="w-5 h-5 mr-2 text-gray-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        {new Date(checkin.timestamp * 1000).toLocaleDateString()}
                      </div>
                      <div className="text-lg font-semibold text-gray-700">
                        {new Date(checkin.timestamp * 1000).toLocaleTimeString()}
                      </div>
                    </div>
                    {index === 0 && (
                      <div className="mt-4 text-base">
                        <span className="px-3 py-1.5 bg-blue-100 text-blue-800 rounded-full font-bold">
                          Latest Check-in
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 text-gray-500">
                <p>No check-ins found in selected time range</p>
              </div>
            )
          ) : (
            <div className="flex justify-center py-10">
              <svg
                className="animate-spin h-6 w-6 text-blue-500"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Live image panel */}
      <div className="flex-1 bg-white rounded-xl p-4 shadow-sm mt-4 md:mt-0 flex flex-col items-center overflow-hidden md:max-h-[calc(100vh-32px)]">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Live Feed</h2>

        <div className="flex-1 w-full h-[calc(100vh-180px)] overflow-hidden rounded-lg bg-gray-100 flex items-center justify-center">
          <img
            src={`http://${import.meta.env.VITE_RPI_HOST}:8000/static/latest_image.jpg?key=${imageKey}`}
            alt="Live Image"
            className="w-full h-full object-cover rounded-md"
          />
        </div>

        <p className="mt-3 text-gray-500 text-xs text-center">Auto-refreshes every second</p>
      </div>
    </div>
  );
}
