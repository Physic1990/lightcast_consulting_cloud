import DriveData from "./DriveData";
import FileSearch from "./FileSearch";
import LCHeader from "./LCHeader";

export default function Home() {
  return (
    <div>
      <div style={{ flex: 1, flexDirection: "row" }}>
        <LCHeader />
        {/* <FileSearch /> */}
      </div>

      <DriveData />
    </div>
  );
}
