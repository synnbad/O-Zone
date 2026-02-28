import { createContext, useContext, useState, ReactNode } from "react";

interface UserProfile {
  name: string;
  age: number;
  hasAsthma: boolean;
  hasAllergies: boolean;
  allergyTypes: string[];
  sensitivityLevel: "low" | "medium" | "high";
  isChild: boolean;
  isElderly: boolean;
}

interface UserContextType {
  profile: UserProfile | null;
  setProfile: (profile: UserProfile) => void;
  isLoggedIn: boolean;
  login: (profile: UserProfile) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const login = (userProfile: UserProfile) => {
    setProfile(userProfile);
    setIsLoggedIn(true);
  };

  const logout = () => {
    setProfile(null);
    setIsLoggedIn(false);
  };

  return (
    <UserContext.Provider value={{ profile, setProfile, isLoggedIn, login, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}
