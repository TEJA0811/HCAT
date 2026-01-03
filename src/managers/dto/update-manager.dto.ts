import { PartialType } from '@nestjs/mapped-types';
import { CreateManagerDto } from './create-manager.dto';
import {
  IsEmail,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
} from 'class-validator';

export class UpdateManagerDto extends PartialType(CreateManagerDto) {
  @IsOptional()
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsOptional()
  @IsNotEmpty()
  @IsEmail()
  email: string;

}
