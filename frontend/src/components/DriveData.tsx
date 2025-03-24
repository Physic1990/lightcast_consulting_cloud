import {
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
} from "@ant-design/icons";
import { Button, Spin, Alert, Modal } from "antd";
import { useEffect, useState } from "react";
import { DriveStructureData } from "../types";

//Create format for processed data object
interface ProcessedData {
  processed_file: string; //Store path to processed file on backend
  hash: string; //Store hash of original file for unique identification
}

//Constant for backend request endpoint
const API_URL = "http://localhost:8000";

export default function DriveData() {
  const [driveData, setDriveData] = useState<DriveStructureData[] | null>([]);
  const [selectPath, setSelectPath] = useState<DriveStructureData[]>([]);
  const [topLevelData, setTopLevelData] = useState<DriveStructureData[]>([]);

  //Set selected file based on ID
  const [selectedFile, setSelectedFile] = useState("");
  const [selectedFileName, setSelectedFileName] = useState(""); // Store file name
  const [status, setStatus] = useState(""); // Model execution status
  const [statusType, setStatusType] = useState<"success" | "error" | "info">(
    "info"
  ); // Status Type
  const [processingTime, setProcessingTime] = useState(0); // Track processing time
  const [loading, setLoading] = useState(false); // Loading state
  const [activeData, setActiveData] = useState<ProcessedData | null>(null);

  //Use to show confirmation modal for actions if not null
  //Modal takes format "(modalName) operation (success ? Successful : Failed)"
  const [confModal, setConfModal] = useState<{
    modalName: string;
    success: boolean;
  } | null>(null);

  // Function to get Drive data
  const getDriveData = async () => {
    await fetch(`${API_URL}/drive_structure`)
      .then((response) => response.json())
      .then((response) => {
        const newData: DriveStructureData[] = [];
        let prevIndent: number = 0;
        const folderLoc = [];

        for (let i = 0; i < response.length; i++) {
          response[i].contents = [];

          if (response[i].indent == 0) {
            newData.push(response[i]);
          } else {
            if (response[i].indent == prevIndent) {
              response[folderLoc[folderLoc.length - 1]].contents.push(
                response[i]
              );
            } else if (response[i].indent > prevIndent) {
              folderLoc.push(i - 1);
              response[folderLoc[folderLoc.length - 1]].contents.push(
                response[i]
              );
            } else {
              folderLoc.pop();
              response[folderLoc[folderLoc.length - 1]].contents.push(
                response[i]
              );
            }
          }
          prevIndent = response[i].indent;
        }
        setDriveData(newData);
        setTopLevelData(newData);
      })
      .catch((error) => console.error("Failed to get Drive data.", error));
  };

  const downloadBlob = (blob: Blob, file_name: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    // the filename you want
    a.download = file_name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
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
      console.log(selectedFileName);
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
      const response = await fetch(`${API_URL}/run-local-model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: selectedFile }),
      });

      const data = await response.json();
      const elapsedTime = (Date.now() - startTime) / 1000; // Calculate time in seconds
      setProcessingTime(elapsedTime);
      setLoading(false);

      // if (data.processed_file) {
      if (data.success) {
        // setStatus(`Model completed in ${elapsedTime.toFixed(2)} sec`);
        setStatus(`File delivered in ${elapsedTime.toFixed(2)} sec`);
        setStatusType("success");
        // setActiveData(data);
      } else {
        setStatus("File failed to deliver.");
        setStatusType("error");
      }
    } catch (error) {
      console.error("Error running model:", error);
      setStatus("Model failed to run.");
      setStatusType("error");
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log("Component mounted. Fetching drive data...");
    getDriveData();
  }, []);

  const handleFileSelect = (file: DriveStructureData) => {
    if (file.type == "folder") {
      setDriveData(file.contents);
      setSelectPath([...selectPath, file]);
    } else {
      setSelectedFile(file.id);
      setSelectedFileName(file.name);
    }
  };

  const exitFolder = () => {
    if (selectPath.length > 1) {
      setDriveData(selectPath[selectPath.length - 2].contents);
    } else {
      setDriveData(topLevelData);
    }
    selectPath.pop();
  };

  const handleDataClose = () => {
    setActiveData(null);
  };

  const handleDataSaveDrive = async () => {
    console.log(activeData?.hash + " saved to Drive");
    try {
      await fetch(`${API_URL}/file_upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_name: activeData?.processed_file,
          mimetype: "application/octet-stream",
          upload_filename: activeData?.processed_file,
          resumable: true,
          chunksize: 262144,
        }),
      })
        .then((response) => response.json())
        .then((response) =>
          setConfModal({ modalName: "Drive", success: response })
        )
        .catch((error) => console.error(error));
    } catch (error) {
      console.error("Error saving file:", error);
    }
  };

  const handleDataSaveLocal = async () => {
    console.log(activeData?.hash + " saved locally");
    await fetch(
      `${API_URL}/file_download?file_path=${activeData?.processed_file}`
    )
      .then((response) => response.blob())
      .then((blob) => downloadBlob(blob, activeData?.processed_file as string))
      .catch((error) => console.error(error));
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
          {/* <Dropdown menu={{ items }}> */}
          <Button
            className="lc_bt"
            size="large"
            style={{ marginBottom: "10px", marginLeft: "-50px" }}
            onClick={() => {
              runModel();
            }}
          >
            Run all_ops.py
          </Button>
          {/* </Dropdown> */}
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
          {selectPath.length > 0 ? (
            <>
              <div
                key={"back"}
                style={{
                  width: "100%",
                  marginLeft: "5%",
                  height: "100%",
                  flex: "1",
                }}
              >
                <Button
                  onClick={() => exitFolder()}
                  style={{
                    scale: "1.5",
                    cursor: "pointer",
                    boxShadow: "none",
                    backgroundColor: "#C62828",
                    color: "white",
                  }}
                >
                  Back
                </Button>
              </div>
              <br />
            </>
          ) : (
            <></>
          )}
          {driveData?.map((file, index) => (
            <>
              <div
                key={file.id}
                style={{
                  marginLeft: "5%",
                  height: "100%",
                  flex: "1",
                }}
              >
                <Button
                  onClick={() => handleFileSelect(file)}
                  style={
                    file.id === selectedFile
                      ? {
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#4e6fcb",
                          color: "white",
                          width: "60%",
                          overflow: "hidden",
                          justifyContent: "flex-start",
                        }
                      : {
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#f4f4f4",
                          width: "60%",
                          overflow: "hidden",
                          justifyContent: "flex-start",
                        }
                  }
                >
                  {file.type == "folder" ? (
                    <FolderOutlined style={{ position: "relative", top: 1 }} />
                  ) : file.type == "file" ? (
                    <FileOutlined style={{ position: "relative", top: 1 }} />
                  ) : (
                    <QuestionOutlined
                      style={{ position: "relative", left: 10, top: 1 }}
                    />
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

      {/* Modal for data display */}
      {/* <Modal
        open={activeData !== null}
        onOk={handleDataSaveLocal}
        onCancel={handleDataClose}
        maskClosable
        footer={[]}
      > */}
      {/* Show processed data - must update with actual visualization */}
      {/* <h2>Processed Data</h2>
        <p>Path: {activeData?.processed_file}</p>
        <p>Hash: {activeData?.hash}</p>
        <script
          src="https://apis.google.com/js/platform.js"
          async
          defer
        ></script>
        <Button
          className="g-savetodrive"
          key="saveToDrive"
          type="primary"
          onClick={handleDataSaveDrive}
        >
          Save to Drive
        </Button>
        <Button key="saveLocal" type="primary" onClick={handleDataSaveLocal}>
          Save Locally
        </Button>
      </Modal> */}

      {/* Modal for event notification */}
      <Modal
        open={confModal !== null}
        onOk={() => setConfModal(null)}
        onCancel={() => setConfModal(null)}
        maskClosable
        footer={[]}
      >
        <h2>
          {confModal?.modalName} Operation{" "}
          {confModal?.success ? "Successful" : "Failed"}
        </h2>
      </Modal>
    </div>
  );
}
