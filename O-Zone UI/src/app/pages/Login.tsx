import { useState } from "react";
import { useNavigate } from "react-router";
import { useUser } from "../context/UserContext";
import { Wind, ChevronRight } from "lucide-react";

export function Login() {
  const navigate = useNavigate();
  const { login } = useUser();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    hasAsthma: false,
    hasAllergies: false,
    allergyTypes: [] as string[],
    sensitivityLevel: "medium" as "low" | "medium" | "high",
  });

  const allergyOptions = [
    "Pollen",
    "Dust Mites",
    "Pet Dander",
    "Mold",
    "Smoke",
    "Chemical Fumes",
  ];

  const toggleAllergy = (allergy: string) => {
    setFormData((prev) => ({
      ...prev,
      allergyTypes: prev.allergyTypes.includes(allergy)
        ? prev.allergyTypes.filter((a) => a !== allergy)
        : [...prev.allergyTypes, allergy],
    }));
  };

  const handleSubmit = () => {
    const age = parseInt(formData.age);
    login({
      name: formData.name,
      age,
      hasAsthma: formData.hasAsthma,
      hasAllergies: formData.hasAllergies,
      allergyTypes: formData.allergyTypes,
      sensitivityLevel: formData.sensitivityLevel,
      isChild: age < 18,
      isElderly: age >= 65,
    });
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-500 p-4 rounded-full">
              <Wind className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-3xl mb-2">O-Zone</h1>
          <p className="text-gray-600">Air Quality Platform</p>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center mb-6">
          <div className="flex gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-2 w-12 rounded-full ${
                  s <= step ? "bg-blue-500" : "bg-gray-200"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-xl mb-4">Welcome! Let's get started</h2>
            <div>
              <label className="block text-sm mb-2 text-gray-700">Your Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your name"
              />
            </div>
            <div>
              <label className="block text-sm mb-2 text-gray-700">Your Age</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your age"
              />
            </div>
            <button
              onClick={() => setStep(2)}
              disabled={!formData.name || !formData.age}
              className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              Next <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Step 2: Health Conditions */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-xl mb-4">Health Information</h2>
            <p className="text-sm text-gray-600 mb-4">
              This helps us provide personalized air quality recommendations
            </p>
            
            <div className="space-y-3">
              <label className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={formData.hasAsthma}
                  onChange={(e) => setFormData({ ...formData, hasAsthma: e.target.checked })}
                  className="w-5 h-5 text-blue-500"
                />
                <div>
                  <div className="text-sm">I have asthma</div>
                  <div className="text-xs text-gray-500">Respiratory condition</div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={formData.hasAllergies}
                  onChange={(e) => setFormData({ ...formData, hasAllergies: e.target.checked })}
                  className="w-5 h-5 text-blue-500"
                />
                <div>
                  <div className="text-sm">I have allergies</div>
                  <div className="text-xs text-gray-500">Air quality sensitivities</div>
                </div>
              </label>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-1 bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 flex items-center justify-center gap-2"
              >
                Next <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Allergy Details & Sensitivity */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-xl mb-4">Sensitivity & Triggers</h2>
            
            {formData.hasAllergies && (
              <div className="mb-4">
                <label className="block text-sm mb-2 text-gray-700">
                  What triggers your allergies?
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {allergyOptions.map((allergy) => (
                    <button
                      key={allergy}
                      onClick={() => toggleAllergy(allergy)}
                      className={`px-3 py-2 rounded-lg border text-sm ${
                        formData.allergyTypes.includes(allergy)
                          ? "bg-blue-500 text-white border-blue-500"
                          : "bg-white text-gray-700 border-gray-300"
                      }`}
                    >
                      {allergy}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm mb-2 text-gray-700">
                Air Quality Sensitivity Level
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(["low", "medium", "high"] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => setFormData({ ...formData, sensitivityLevel: level })}
                    className={`px-4 py-3 rounded-lg border capitalize ${
                      formData.sensitivityLevel === level
                        ? "bg-blue-500 text-white border-blue-500"
                        : "bg-white text-gray-700 border-gray-300"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                className="flex-1 bg-green-500 text-white py-3 rounded-lg hover:bg-green-600"
              >
                Get Started
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
