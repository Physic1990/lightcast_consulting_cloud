import React, { useEffect, useState } from "react";

const MembersContext = React.createContext({
  members: [],
  fetchMembers: () => {},
});

export default function Members() {
  const [members, setMembers] = useState([]);

  const fetchMembers = async () => {
    const response = await fetch("https://localhost:8000/members");
    const members = await response.json();
    setMembers(members.data);
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  return (
    <MembersContext.Provider value={{ members, fetchMembers }}>
      {members.map((member) => (
        <p>{member}</p>
      ))}
    </MembersContext.Provider>
  );
}
