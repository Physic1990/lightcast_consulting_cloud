import {
  CloseOutlined,
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
} from "@ant-design/icons";
import { Breadcrumb, Button, Spin, Alert, Popover } from "antd";
import { useEffect, useState } from "react";
import { DriveStructureData } from "../types";
import { ItemType } from "antd/es/breadcrumb/Breadcrumb";

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

  //Authentication failed; show login button
  const [authError, setAuthError] = useState(false);

  //Scripts found in the local folder
  const [scripts, setScripts] = useState<string[]>([]);

  //Breadcrumb navigation for Drive files
  const [breadcrumbs, setBreadcrumbs] = useState<ItemType[]>([
    { title: "Home" },
  ]);

  //Use to show context menu for individual files
  const [contextMenu, setContextMenu] = useState<DriveStructureData | null>(
    null
  );

  // Function to get Drive data
  const getDriveData = async () => {
    await fetch(`${API_URL}/drive_structure`, {
      credentials: "include",
    })
      .then((response) => response.json())
      .then((response) => {
        const newData: DriveStructureData[] = [];
        let prevIndent: number = 0;
        const folderLoc = [];

        if ("detail" in response && response["detail"] == "Not authenticated") {
          console.error("Could not retrieve Drive data, unauthenticated.");
          setAuthError(true);
          return;
        }

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

  // Function to run the model
  const runModel = async (selectedScript: string) => {
    if (!selectedFile) {
      alert("Please select a file first!");
      setStatus("No file selected. Please choose a valid file.");
      setStatusType("error");
      return;
    }

    //Declare regex for file names
    // prettier-ignore
    const filename_format = new RegExp(".*\.xl..?");

    // Check if the selected file is an Excel file (.xl..?)
    if (!filename_format.test(selectedFileName)) {
      setStatus("Only Excel files can be processed.");
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
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: selectedFile, script: selectedScript }),
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

  //Get scripts stored on the local system for display
  const getScripts = async () => {
    await fetch(`${API_URL}/script_folder`, {
      credentials: "include",
    })
      .then((response) => response.json())
      .then((response) => setScripts(response))
      .catch((error) => console.error(error));
  };

  //Set selectPath and reflect it in breadcrumbs
  const handleSelectPath = (newPath: DriveStructureData[]) => {
    setSelectPath(newPath);

    const locBreadcrumbs: ItemType[] = [];
    locBreadcrumbs.push({
      title: (
        <Button
          style={{ all: "unset", cursor: "pointer" }}
          onClick={() => rollBackCrumbs("Home")}
        >
          Home
        </Button>
      ),
      // title: "Home",
    });
    newPath.forEach((element) => {
      locBreadcrumbs.push({
        title: (
          <Button
            style={{ all: "unset", cursor: "pointer" }}
            onClick={() => rollBackCrumbs(element.name)}
          >
            {element.name}
          </Button>
        ),
        // title: `${element.name}`,
      });
    });
    setBreadcrumbs(locBreadcrumbs);
  };

  useEffect(() => {
    console.log("Component mounted. Fetching drive data...");
    getDriveData();

    getScripts();
  }, []);

  const handleFileSelect = (file: DriveStructureData) => {
    if (file.type == "folder") {
      setDriveData(file.contents);
      handleSelectPath([...selectPath, file]);
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
    handleSelectPath(selectPath.slice(0, selectPath.length - 1));
  };

  //Run through login flow
  const loginFlow = async () => {
    await fetch(`${API_URL}/auth/login`, {
      credentials: "include",
    })
      .then((response) => response.json())
      .then((response) => window.open(response["authorization_url"]))
      .catch((error) => console.error(error));
  };

  //Exit folders until the correct one (or Home) has been reached; NOT CURRENTLY WORKING, BUTTONS CREATED FOR THIS ARE ONE REFRESH BEHIND
  const rollBackCrumbs = (targetFolder: string) => {
    let folderDepth = selectPath.length;
    let folderName =
      folderDepth > 0 ? selectPath[folderDepth - 1].name.toString() : "Home";

    while (folderDepth > 0 && folderName !== targetFolder) {
      folderDepth -= 1;
      console.log(folderDepth);
      folderName =
        folderDepth > 0 ? selectPath[folderDepth - 1].name.toString() : "Home";
      console.log(folderName);
    }

    if (folderDepth > 0) {
      setDriveData(selectPath[folderDepth - 1].contents);
      handleSelectPath(selectPath.slice(0, folderDepth));
    } else {
      setDriveData(topLevelData);
      handleSelectPath([]);
    }
  };

  //Right click handling for file buttons
  const handleFileContext = (
    e: React.MouseEvent<HTMLElement>,
    file: DriveStructureData
  ) => {
    e.preventDefault();
    if (contextMenu) {
      setContextMenu(null);
    } else {
      setContextMenu(file);
    }
  };

  //Allow copying file path from button
  const handlePathCopy = (fileName: string) => {
    let prefix = "/";
    if (selectPath.length > 0) {
      selectPath.forEach((item) => {
        prefix = prefix + item.name + "/";
      });
    }
    navigator.clipboard.writeText(prefix + fileName);
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      {/* Breadcrumb navigation bar */}
      <Breadcrumb items={breadcrumbs} style={{ fontSize: "1.5em" }} />
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
          {scripts.length > 0 ? (
            scripts.map((script) => (
              <li style={{ listStyleType: "none" }}>
                <Button
                  className="lc_bt"
                  size="large"
                  style={{ marginBottom: "10px", marginLeft: "-50px" }}
                  onClick={() => {
                    runModel(script);
                  }}
                >
                  Run {script}
                </Button>
              </li>
            ))
          ) : (
            <p style={{ listStyleType: "none", marginLeft: "-20%" }}>
              Ensure you have selected a folder of Python scripts through the
              local helper, then refresh!
            </p>
          )}
          {}
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
          {authError ? (
            <div style={{ flex: "1" }}>
              {/* Bit obnoxious for now, should be changed */}
              <p>Please</p>
              <Button style={{ scale: "2" }} type="primary" onClick={loginFlow}>
                Log In
              </Button>
              <p>to continue!</p>
            </div>
          ) : (
            driveData?.map((file, index) => (
              <>
                <div
                  key={file.id}
                  style={{
                    marginLeft: "5%",
                    height: "100%",
                    flex: "1",
                  }}
                >
                  <Popover
                    content={
                      <div style={{ textAlign: "center" }}>
                        <Button onClick={() => handlePathCopy(file.name)}>
                          Copy File Path
                        </Button>
                        <br />
                        <Button
                          style={{
                            borderStyle: "hidden",
                            cursor: "pointer",
                            padding: "0",
                            margin: "0",
                            right: "0",
                          }}
                          onClick={() => setContextMenu(null)}
                        >
                          <CloseOutlined
                            style={{ margin: "0", right: "0px" }}
                          />
                        </Button>
                      </div>
                    }
                    open={contextMenu?.id === file.id}
                  >
                    <Button
                      onClick={() => handleFileSelect(file)}
                      onContextMenu={(e) => handleFileContext(e, file)}
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
                        <FolderOutlined
                          style={{ position: "relative", top: 1 }}
                        />
                      ) : file.type == "file" ? (
                        <FileOutlined
                          style={{ position: "relative", top: 1 }}
                        />
                      ) : (
                        <QuestionOutlined
                          style={{ position: "relative", left: 10, top: 1 }}
                        />
                      )}
                      <br />
                      {file.name}
                    </Button>
                  </Popover>
                </div>
                {(index + 1) % 3 === 0 ? (
                  <div
                    style={{ flexBasis: "100%", height: "0", marginTop: "5%" }}
                  />
                ) : (
                  <></>
                )}
              </>
            ))
          )}
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
