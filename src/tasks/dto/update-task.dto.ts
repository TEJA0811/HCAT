import { PartialType } from '@nestjs/mapped-types';
import { CreateTaskDto } from './create-task.dto';
import { IsNotEmpty, IsString, IsNumber, IsEnum, IsOptional, IsDateString, Min, Max } from 'class-validator';
import { TaskDifficulty, TaskStatus } from '../../utils/constant';

export class UpdateTaskDto extends PartialType(CreateTaskDto) {
  @IsOptional()
  @IsNotEmpty()
  @IsString()
  title: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsOptional()
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

  @IsOptional()
  @IsNotEmpty()
  @IsNumber()
  project_id: number;

  @IsOptional()
  @IsNotEmpty()
  @IsNumber()
  assigned_by: number;
}