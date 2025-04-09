//This component should act as a frontend for the Drive search functionality
//CURRENTLY NONFUNCTIONAL

// import { Form, FormProps, Input } from "antd";
// import { ChangeEventHandler } from "react";

// interface FieldType {
//   fileName: string;
// }

// export default function FileSearch() {
//   const searchDrive = async (value: string) => {
//     //Fetch and read search responses
//     const itemStream = await fetch(
//       `http://localhost:8000/search?file_name=${Object.values(value)}`
//     ).then((response) => response?.body?.getReader());
//     console.log(itemStream);
//     const items = await itemStream?.read();
//     console.log(items);

//     //Iterate through retrieved items
//     let itemsLen = (await items)?.value?.length;
//     const itemType = typeof itemsLen;
//     itemsLen = itemType === undefined ? 0 : itemsLen;
//     for (let i = 0; i < itemsLen; i++) {
//       console.log(`i is ${itemsLen}`);
//     }
//   };

//   return (
//     <Input
//       placeholder="Search Your Drive"
//       style={{ width: "50%" }}
//       onChange={(e) => searchDrive(e.target.value)}
//     ></Input>
//   );
// }
