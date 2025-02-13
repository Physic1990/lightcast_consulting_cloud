import Icon, {
  EditFilled,
  FileOutlined,
  FolderOutlined,
  QuestionOutlined,
  StarFilled,
  ToolFilled,
} from "@ant-design/icons";
import { Button, Breadcrumb, Dropdown, MenuProps } from "antd";
import { useEffect, useState } from "react";

export default function DriveData() {
  const [driveData, setDriveData] = useState([]);
  const [selectPath, setSelectPath] = useState([]);
  var topLevelData;

  //Set selected file based on ID
  const [selectedFile, setSelectedFile] = useState("");
  // Function to get Drive data
  const getDriveData = async () => {
    await fetch("http://localhost:8000/drive_structure")
      .then((response) => response.json())
      .then((response) => {
        var newData = [];
        var prevIndent : number = 0;
        var folderLoc = [];

        for(var i = 0; i < response.length; i++) {
          response[i].contents = [];

          if(response[i].indent == 0) {
            newData.push(response[i]);
          } else {
            if(response[i].indent == prevIndent) {
              response[folderLoc[folderLoc.length - 1]].contents.push(response[i]);            
            } else if(response[i].indent > prevIndent) {
              folderLoc.push(i - 1);
              response[folderLoc[folderLoc.length - 1]].contents.push(response[i]);
            } else {
              folderLoc.pop();
              response[folderLoc[folderLoc.length - 1]].contents.push(response[i]);
            }
          }
          prevIndent = response[i].indent;
        }
        setDriveData(newData);
        topLevelData = newData;
      })
      .catch(() => console.error("Failed to get Drive data."));
  };

  // Function to run the model
  const runModel = async () => {
    await fetch("http://localhost:8000/run-local-model", {
      method: "POST",
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

  const handleFileSelect = (file) => {
    console.log(selectedFile);
    if(file.type == 'folder') {
      setDriveData(file.contents);
      setSelectPath([...selectPath, file])
    } else {
      console.log(file.id);
      setSelectedFile(file.id);
    }
  };

  const exitFolder = () => {
    if(selectPath.length > 1) {
      setDriveData(selectPath[selectPath.length - 2].contents);
    } else {
      getDriveData();
    }
    selectPath.pop();
  }

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
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
          }}
        >
          { selectPath.length > 0 ? 
            <>
            <div
              key={'back'}
              style={{
                width: "20%",
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
                  color: "white"
                }}>
                  Back
                </Button>
              </ div>
              <br />
              </>
          : <></>}
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
                  onClick={() => handleFileSelect(file)}
                  style={
                    file.id == selectedFile
                      ? {
                          // border: "none",
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#4e6fcb",
                          color: "white",
                        }
                      : {
                          // border: "none",
                          scale: "1.5",
                          cursor: "pointer",
                          boxShadow: "none",
                          backgroundColor: "#f4f4f4"
                        }
                  }
                >
                  {file.type == "folder" ? (
                    <FolderOutlined />
                  ) : file.type == "file" ? (
                    <FileOutlined />
                  ) : (
                    <QuestionOutlined />
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
    </div>
  );
}
