import { createBrowserRouter } from "react-router";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ActivityPage } from "./pages/Activity";
import { Globe } from "./pages/Globe";
import { Trends } from "./pages/Trends";
import { CleanRoom } from "./pages/CleanRoom";
import { Chat } from "./pages/Chat";
import { Safety } from "./pages/Safety";
import { Pollutants } from "./pages/Pollutants";
import { Notifications } from "./pages/Notifications";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Login,
  },
  {
    path: "/dashboard",
    Component: Dashboard,
  },
  {
    path: "/activity",
    Component: ActivityPage,
  },
  {
    path: "/globe",
    Component: Globe,
  },
  {
    path: "/trends",
    Component: Trends,
  },
  {
    path: "/clean-room",
    Component: CleanRoom,
  },
  {
    path: "/chat",
    Component: Chat,
  },
  {
    path: "/safety",
    Component: Safety,
  },
  {
    path: "/pollutants",
    Component: Pollutants,
  },
  {
    path: "/notifications",
    Component: Notifications,
  },
]);
