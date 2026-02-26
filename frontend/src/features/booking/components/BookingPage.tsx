// src/features/booking/components/BookingPage.tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { initiateCall } from "../services/bookingService";
import Logout from "../../auth/components/Logout";

export default function BookingPage() {
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    setMessage(null);
    setIsLoading(true);

    try {
      const res = await initiateCall(phone);
      setMessage({ text: `Call initiated successfully. SID: ${res.call_sid}`, isError: false });
      setPhone("");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Failed to initiate call";
      setMessage({ text: String(msg), isError: true });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      {/* Header */}
      <header className="w-full bg-white border-b border-blue-100 shadow-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-md group-hover:bg-blue-700 transition-colors">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <span className="text-xl font-bold tracking-tight text-blue-900">iClinic</span>
          </Link>
          {/* Logout top-right */}
          <Logout />
        </div>
      </header>

      {/* Main */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Stats card strip */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              { label: "Today's Calls", value: "—" },
              { label: "Appointments", value: "—" },
              { label: "Patients", value: "—" },
            ].map((stat) => (
              <div key={stat.label}
                className="bg-white rounded-xl border border-blue-100 p-4 text-center shadow-sm">
                <p className="text-lg font-bold text-blue-700">{stat.value}</p>
                <p className="text-xs text-blue-400 mt-0.5">{stat.label}</p>
              </div>
            ))}
          </div>

          {/* Booking card */}
          <div className="bg-white rounded-2xl shadow-lg border border-blue-100 p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-blue-900">Book Appointment</h2>
                <p className="text-xs text-blue-400">Initiate a call to schedule patient visit</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="phone"
                  className="block text-sm font-medium text-blue-800 mb-1.5">
                  Patient Phone Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                    <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </div>
                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91XXXXXXXXXX"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blue-200 bg-blue-50/50 text-blue-900 placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition text-sm"
                  />
                </div>
              </div>

              {message && (
                <div className={`flex items-start gap-2 rounded-xl px-4 py-3 border ${
                  message.isError
                    ? "bg-red-50 border-red-200"
                    : "bg-green-50 border-green-200"
                }`}>
                  <svg className={`w-4 h-4 mt-0.5 flex-shrink-0 ${message.isError ? "text-red-500" : "text-green-500"}`}
                    fill="currentColor" viewBox="0 0 20 20">
                    {message.isError ? (
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    ) : (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    )}
                  </svg>
                  <p className={`text-sm ${message.isError ? "text-red-600" : "text-green-700"}`}>
                    {message.text}
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5 rounded-xl transition-colors shadow-sm text-sm flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Calling...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    Call Patient
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}