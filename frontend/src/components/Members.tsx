//Example component to demonstrate React-FastAPI interactions, largely instructed by https://testdriven.io/blog/fastapi-react

import React, { useEffect, useState } from "react";
import { MembersContextProps } from "../types";
import { Form, FormProps, Input } from "antd";

const MembersContext = React.createContext({
  members: [],
  fetchMembers: () => {},
} as MembersContextProps);

export default function Members() {
  const [members, setMembers] = useState([]);

  const fetchMembers = async () => {
    const response = await fetch("http://localhost:8000/members");
    const members = await response.json();
    setMembers(members.data);
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  function AddMember() {
    interface FieldType {
      name?: string;
    }

    const handleSubmit: FormProps<FieldType>["onFinish"] = (value: object) => {
      console.log(value);
      const newMember = {
        id: members.length + 1,
        item: Object.values(value)[0],
      };

      fetch("http://localhost:8000/members", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newMember),
      }).then(fetchMembers);
    };

    return (
      <>
        <Form onFinish={handleSubmit}>
          <Form.Item<string>
            // label="Member Name"
            name="name"
            rules={[{ required: true, message: "Add a member" }]}
          >
            <Input />
          </Form.Item>
        </Form>
      </>
    );
  }
  const deleteMember = async ({ memberID }: { memberID: number }) => {
    console.log(`Attempting to delete member #${memberID}`);
    await fetch(`http://localhost:8000/members/${memberID}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: memberID }),
    });
    await fetchMembers();
  };

  return (
    <>
      <MembersContext.Provider value={{ members, fetchMembers }}>
        {members.map((member) => (
          <p key={member.id} onClick={() => deleteMember(member.id)}>
            {member.item}
          </p>
        ))}
      </MembersContext.Provider>
      <AddMember />
    </>
  );
}
