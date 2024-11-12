import { Button } from "antd";

export default function LCHeader() {
  return (
    <div>
      <div style={{ width: "100%", marginRight: "auto" }}>
        <img src="/src/assets/LCLogo.png" width={250} />
      </div>
      <div style={{ marginTop: "20px" }}>
        <Button className="lc_bt" size="large">
          Work on a Project
        </Button>
      </div>
    </div>
  );
}
