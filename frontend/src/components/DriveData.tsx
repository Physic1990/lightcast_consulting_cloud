import Icon, {
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
} from "@ant-design/icons";
import { Button } from "antd";
import { useEffect, useState } from "react";

export default function DriveData() {
  const [driveData, setDriveData] = useState([]);

  const getDriveData = async () => {
    await fetch("http://localhost:8000/drive_data?include_trashed=True")
      .then((response) => response.json())
      .then((response) => setDriveData(response))
      .catch(() => console.error("Failed to get Drive data."));
  };

  useEffect(() => {
    getDriveData();
  }, []);

  return (
    <div>
      <h2 style={{ textAlign: "center", scale: "1.3" }}>
        Select a State and School
      </h2>
      <div
        style={{
          display: "inline-block",
          width: "20%",
          backgroundColor: "#f7f7f7",
        }}
      >
        <ul style={{ textAlign: "center" }}>
          <Button className="lc_bt" size="large">
            Model Type 1
          </Button>
          <br />
          <Button className="lc_bt" size="large">
            Model Type 2
          </Button>
          <br />
          <Button className="lc_bt" size="large">
            Model Type 3
          </Button>
        </ul>
      </div>
      <div
        style={{
          display: "inline-block",
          width: "80%",
          textAlign: "center",
        }}
      >
        {/* <h2>Drive Data</h2> */}
        <div style={{ display: "flex" }}>
          {driveData.map((file) => (
            <div
              key={file.id}
              style={{
                width: "30%",
                background: "#f7f7f7",
                marginLeft: "5%",
                height: "100%",
              }}
            >
              {file.kind == "drive#folder" ? (
                <FolderOutlined style={{ scale: "2" }} />
              ) : file.kind == "drive#file" ? (
                <FileOutlined style={{ scale: "2" }} />
              ) : (
                <QuestionOutlined style={{ scale: "2" }} />
              )}
              <br />
              {file.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
