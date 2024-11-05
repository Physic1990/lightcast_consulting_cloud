import DriveData from "./DriveData";
import FileSearch from "./FileSearch";
import LCHeader from "./LCHeader";

export default function Home() {
  return (
    <div>
      {/* <FileSearch /> */}
      <LCHeader />
      <div style={{ clear: "both" }}></div>
      <DriveData />
      {/* <Header />
      <Members /> */}
    </div>
  );
}
