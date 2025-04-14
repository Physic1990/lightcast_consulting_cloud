import DriveData from "./DriveData";
import LCHeader from "./LCHeader";

//Display the home page for the Consulting Cloud frontend
export default function Home() {
  return (
    <div>
      <div style={{ flex: 1, flexDirection: "row" }}>
        <LCHeader />
      </div>

      <DriveData />
    </div>
  );
}
