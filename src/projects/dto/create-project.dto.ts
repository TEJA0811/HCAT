import { IsArray, IsNotEmpty, IsNumber, IsOptional, IsString } from 'class-validator';
import { statusType } from '../../utils/constant';

export class CreateProjectDto {
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsNotEmpty()
  @IsString()
  description: string;

  @IsNotEmpty()
  @IsString()
  status: statusType;

  @IsNotEmpty()
  start_date: Date;

  @IsOptional()
  end_date: Date;

  @IsOptional()
  @IsArray()
  @IsNumber({}, { each: true })
  manager_ids?: number[];

  // @IsOptional()
  // @IsArray()
  // @IsNumber({}, { each: true })
  // user_ids?: number[];
}
