//This component should act as a frontend for the Drive search functionality
//CURRENTLY NONFUNCTIONAL

import { Form, FormProps, Input } from "antd";

interface FieldType {
  fileName: string;
}

export default function FileSearch() {
  const searchDrive: FormProps<FieldType>["onFinish"] = async (value) => {
    //Fetch and read search responses
    const itemStream = await fetch(
      `http://localhost:8000/search?file_name=${Object.values(value)[0]}`
    ).then((response) => response?.body?.getReader());
    console.log(itemStream);
    const items = await itemStream?.read();
    console.log(items);

    //Iterate through retrieved items
    let itemsLen = (await items)?.value?.length;
    const itemType = typeof itemsLen;
    itemsLen = itemType === undefined ? 0 : itemsLen;
    for (let i = 0; i < itemsLen; i++) {
      console.log(`i is ${itemsLen}`);
    }
  };

  return (
    <Form onFinish={searchDrive}>
      <Form.Item name="fileName">
        <Input placeholder="Search Your Drive"></Input>
      </Form.Item>
    </Form>
  );
}
