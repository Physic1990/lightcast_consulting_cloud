import Icon, {
  EditFilled,
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
  StarFilled,
  ToolFilled,
} from "@ant-design/icons";
import { Button, Dropdown, MenuProps, Spin, Alert } from "antd";
import { useEffect, useState } from "react";

export default function DriveData() {
  const [driveData, setDriveData] = useState([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [selectedFileName, setSelectedFileName] = useState(""); // Store file name
  const [status, setStatus] = useState(""); // Model execution status
  const [statusType, setStatusType] = useState<"success" | "error" | "info">("info"); // Status Type
  const [processingTime, setProcessingTime] = useState(0); // Track processing time
  const [loading, setLoading] = useState(false); // Loading state

  // Function to get Drive data
  const getDriveData = async () => {
    console.log("Fetching drive data...");
    await fetch("http://localhost:8000/drive_data?include_trashed=True")
      .then((response) => response.json())
      .then((response) => {
        setDriveData(response);
        console.log("Drive data loaded:", response);
      })
      .catch((error) => console.error("Failed to get Drive data.", error));
  };

  // Function to run the model
  const runModel = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      setStatus("No file selected. Please choose a valid file.");
      setStatusType("error");
      return;
    }

    // Check if the selected file is an Excel file (.xlsx)
    if (!selectedFileName.endsWith(".xlsx")) {
      setStatus("Only .xlsx files can be processed.");
      setStatusType("error");
      return;
    }

    console.log(`Sending file to backend: ${selectedFile}`);
    setLoading(true);
    setStatus("Running model...");
    setStatusType("info");
    setProcessingTime(0);
    const startTime = Date.now(); // Track start time

    try {
      const response = await fetch("http://localhost:8000/run-local-model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: selectedFile }),
      });

      const data = await response.json();
      const elapsedTime = (Date.now() - startTime) / 1000; // Calculate time in seconds
      setProcessingTime(elapsedTime);
      setLoading(false);

      if (data.processed_file) {
        setStatus(`Model completed in ${elapsedTime.toFixed(2)} sec`);
        setStatusType("success");
      } else {
        setStatus("Model failed to run.");
        setStatusType("error");
      }
    } catch (error) {
      console.error("Error running model:", error);
      setStatus("Model failed to run.");
      setStatusType("error");
      setLoading(false);
    }
  };

  // Menu items with handlers
  const items: MenuProps["items"] = [
    {
      key: "1",
      label: (
        <p
          onClick={() => {
            console.log("Run Model clicked");
            runModel();
          }}
          style={{ cursor: "pointer" }}
        >
          <ToolFilled style={{ marginRight: "10px" }} />
          Run the Model
        </p>
      ),
    },
    {
      key: "2",
      label: (
        <p onClick={() => console.log("Run Draft Operation clicked")}>
          <EditFilled style={{ marginRight: "10px" }} />
          Run Draft Operation
        </p>
      ),
    },
    {
      key: "3",
      label: (
        <p onClick={() => console.log("Run Deliverable Preparation clicked")}>
          <StarFilled style={{ marginRight: "10px" }} />
          Run Deliverable Preparation
        </p>
      ),
    },
  ];

  useEffect(() => {
    console.log("Component mounted. Fetching drive data...");
    getDriveData();
  }, []);

  const handleFileSelect = (id: string, name: string) => {
    console.log(`File selected: ID=${id}, Name=${name}`);
    setSelectedFile(id);
    setSelectedFileName(name);
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h2>Run Model on Selected File</h2>

      {/* Drive Data Section */}
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
              onClick={() => console.log("Model Type 1 clicked")}
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
              onClick={() => console.log("Model Type 2 clicked")}
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
              onClick={() => console.log("Model Type 3 clicked")}
            >
              Model Type 3
            </Button>
          </Dropdown>
        </ul>
      </div>

      {/* File List Display */}
      <div
        style={{
          display: "inline-block",
          width: "80%",
          textAlign: "center",
          verticalAlign: "top",
          marginTop: "25px",
        }}
      >
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
          }}
        >
          {driveData.map((file, index) => (
            <>
              <div
                key={file.id}
                style={{
                  width: "20%",
                  marginLeft: "5%",
                  height: "100%",
                  flex: "1",
                }}
              >
                <Button
                  onClick={() => handleFileSelect(file.id, file.name)}
                  style={
                    file.id === selectedFile
                      ? {
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#4e6fcb",
                          color: "white",
                        }
                      : {
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#f4f4f4",
                        }
                  }
                >
                  {file.kind === "drive#folder" ? (
                    <FolderOutlined />
                  ) : file.kind === "drive#file" ? (
                    <FileOutlined />
                  ) : (
                    <QuestionOutlined style={{ scale: "2" }} />
                  )}
                  <br />
                  {file.name}
                </Button>
              </div>
              {(index + 1) % 3 === 0 ? (
                <div
                  style={{ flexBasis: "100%", height: "0", marginTop: "5%" }}
                />
              ) : (
                <></>
              )}
            </>
          ))}
        </div>
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div style={{ marginTop: "15px" }}>
          <Spin size="large" />
        </div>
      )}

      {/* Model Execution Status with Error Highlighting */}
      {status && (
        <div style={{ marginTop: "15px" }}>
          <Alert
            message={status}
            type={statusType}
            showIcon
            style={statusType === "error" ? { backgroundColor: "#f8d7da" } : {}}
          />
        </div>
      )}
    </div>
  );
}
