import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';
import {
  IsEmail,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
} from 'class-validator';
import { UserType } from 'src/utils/constant';

export class UpdateUserDto extends PartialType(CreateUserDto) {
  @IsOptional()
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsOptional()
  @IsNotEmpty()
  @IsEmail()
  email: string;

  @IsOptional()
  @IsNotEmpty()
  password: string;

  @IsOptional()
  @IsString()
  role: UserType;

  @IsOptional()
  @IsNotEmpty()
  @IsNumber()
  reports_to: number;

  @IsOptional()
  @IsNotEmpty()
  @IsNumber()
  team_id: number;
}
