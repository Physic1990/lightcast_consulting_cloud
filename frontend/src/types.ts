export interface MembersContextProps {
  members:
    | never[]
    | {
        id: number;
        name: string;
      }[];
  fetchMembers: () => void;
}

export interface DriveStructureData {
  name: string;
  id: string;
  type: string;
  indent: number;
  folder_id: string;
  contents: DriveStructureData[] | null;
}
