import { PartialType } from '@nestjs/mapped-types';
import { CreateProjectDto } from './create-project.dto';
import { IsNotEmpty, IsNumber, IsOptional, IsString } from 'class-validator';
import { statusType } from '../../utils/constant';

export class UpdateProjectDto extends PartialType(CreateProjectDto) {
  @IsOptional()
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsOptional()
  @IsString()
  description: string;

  @IsOptional()
  @IsNotEmpty()
  @IsString()
  status: statusType;

  @IsOptional()
  @IsNotEmpty()
  start_date: Date;

  @IsOptional()
  end_date: Date;
}
