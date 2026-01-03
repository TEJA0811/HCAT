import { IsNotEmpty, IsString, IsNumber, IsEnum, IsOptional, IsDateString, Min, Max } from 'class-validator';
import { TaskDifficulty, TaskStatus } from '../../utils/constant';

export class CreateTaskDto {
  @IsNotEmpty()
  @IsString()
  title: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsNotEmpty()
  @IsNumber()
  assignee_id: number; // User ID

  @IsOptional()
  @IsNumber()
  story_points?: number;

  @IsOptional()
  @IsString()
  sprint?: string;

  @IsOptional()
  deadline?: Date;

  @IsOptional()
  @IsEnum(TaskDifficulty)
  difficulty?: TaskDifficulty;

  @IsOptional()
  @IsEnum(TaskStatus)
  status?: TaskStatus;

  @IsNotEmpty()
  @IsNumber()
  project_id: number;

  @IsNotEmpty()
  @IsNumber()
  assigned_by: number;
}