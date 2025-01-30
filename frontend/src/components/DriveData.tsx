import Icon, {
  EditFilled,
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
  StarFilled,
  ToolFilled,
} from "@ant-design/icons";
import { Button, Dropdown, MenuProps } from "antd";
import { useEffect, useState } from "react";

export default function DriveData() {
  const [driveData, setDriveData] = useState([]);

  // Function to get Drive data
  const getDriveData = async () => {
    await fetch("http://localhost:8000/drive_data?include_trashed=True")
      .then((response) => response.json())
      .then((response) => setDriveData(response))
      .catch(() => console.error("Failed to get Drive data."));
  };

  // Function to run the model
  const runModel = async () => {
    // try {
    //   const response = await fetch("http://localhost:8000/run-local-model", {
    //     method: "POST",
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //   });
    //   const data = await response.json();
    //   console.log(data);
    //   alert(`Processed Text: ${data.processed_text}`);
    // } catch (error) {
    //   console.error("Error:", error);
    //   alert("Failed to run the model.");
    // }

    await fetch("http://localhost:8000/run-local-model", {
      method: "POST",
      mode: "no-cors",
      // headers: { "Access-Control-Allow-Origin": "*" },
    })
      .then((response) => response.json())
      .then((response) => console.log(response))
      .catch((error) => {
        console.error("Error:", error);
        alert("Failed to run the model.");
      });
  };

  // Menu items with handlers
  const items: MenuProps["items"] = [
    {
      key: "1",
      label: (
        <p onClick={runModel} style={{ cursor: "pointer" }}>
          <ToolFilled style={{ marginRight: "10px" }} />
          Run the Model
        </p>
      ),
    },
    {
      key: "2",
      label: (
        <p>
          <EditFilled style={{ marginRight: "10px" }} />
          Run Draft Operation
        </p>
      ),
    },
    {
      key: "3",
      label: (
        <p>
          <StarFilled style={{ marginRight: "10px" }} />
          Run Deliverable Preparation
        </p>
      ),
    },
  ];

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
        <ul style={{ textAlign: "center", alignContent: "center" }}>
          <Dropdown menu={{ items }}>
            <Button
              className="lc_bt"
              size="large"
              style={{ marginBottom: "10px", marginLeft: "-50px" }}
            >
              Model Type 1
            </Button>
          </Dropdown>
          <br />
          <Dropdown menu={{ items }}>
            <Button
              className="lc_bt"
              size="large"
              style={{ marginBottom: "10px", marginLeft: "-50px" }}
            >
              Model Type 2
            </Button>
          </Dropdown>
          <br />
          <Dropdown menu={{ items }}>
            <Button
              className="lc_bt"
              size="large"
              style={{ marginLeft: "-50px" }}
            >
              Model Type 3
            </Button>
          </Dropdown>
        </ul>
      </div>
      <div
        style={{
          display: "inline-block",
          width: "80%",
          textAlign: "center",
          verticalAlign: "top",
          marginTop: "25px",
        }}
      >
        <div style={{ display: "flex" }}>
          {driveData.map((file) => (
            <div
              key={file.id}
              style={{
                width: "30%",
                marginLeft: "5%",
                height: "100%",
              }}
            >
              {file.kind === "drive#folder" ? (
                <FolderOutlined style={{ scale: "2" }} />
              ) : file.kind === "drive#file" ? (
                <FileOutlined style={{ scale: "2", cursor: "pointer" }} />
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
