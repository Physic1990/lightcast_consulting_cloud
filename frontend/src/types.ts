export interface MembersContextProps {
  members:
    | never[]
    | {
        id: number;
        name: string;
      }[];
  fetchMembers: () => void;
}
