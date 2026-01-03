import { IsNotEmpty, IsNumber, IsOptional, IsString } from 'class-validator';

export class CreateTeamDto {
  @IsOptional()
  @IsString()
  team_name: string;

  @IsNotEmpty()
  @IsNumber()
  manager_id: number;
}
