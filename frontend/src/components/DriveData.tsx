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

  //Set selected file based on ID
  const [selectedFile, setSelectedFile] = useState("");

  const getDriveData = async () => {
    await fetch("http://localhost:8000/drive_data?include_trashed=True")
      .then((response) => response.json())
      .then((response) => {
        setDriveData(response);
        // console.log(response);
      })
      .catch(() => console.error("Failed to get Drive data."));
  };

  const items: MenuProps["items"] = [
    {
      key: "1",
      label: (
        <p>
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

  const handleFileSelect = (id: string) => {
    console.log(selectedFile);
    console.log(id);
    setSelectedFile(id);
  };

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
                {/* <Button style={{all: "unset"}}> */}
                {/* <Button onClick={() => handleFileSelect(file.id)} color={file.id == selectedFile ? "primary" : "default"} style={{border: "none", scale: "2", cursor: "pointer", boxShadow: "none"}}> */}
                <Button
                  onClick={() => handleFileSelect(file.id)}
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
                  {file.kind == "drive#folder" ? (
                    <FolderOutlined />
                  ) : file.kind == "drive#file" ? (
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
    </div>
  );
}
