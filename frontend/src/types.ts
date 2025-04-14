//Type for files retrieved from Google Drive
export interface DriveStructureData {
  name: string;
  id: string;
  type: string;
  indent: number;
  folder_id: string;
  contents: DriveStructureData[] | null;
}
