import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Res,
  HttpStatus,
  Put,
  ConflictException,
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post('create')
  async create(@Body() createUserDto: CreateUserDto) {
    const existingUser = await this.usersService.findBy({
      where: { email: createUserDto.email },
    });

    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }
    const user = await this.usersService.create(createUserDto);
    return {
      message: 'User added',
      data: user,
    };
  }

  @Get()
  async findAll() {
    const user = await this.usersService.findAll();
    return {
      message: 'User list',
      data: user,
    };
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const user = await this.usersService.findone(+id);
    if (!user) {
      return {
        message: 'user not found',
        data: {},
      };
    }
    return {
      message: 'User found',
      data: user,
    };
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    const existingUser = await this.usersService.findBy({
      where: { email: updateUserDto.email },
    });

    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }
    const user = await this.usersService.findone(+id);

    if (!user) {
      return {
        message: 'user not found',
        data: {},
      };
    }
    await this.usersService.update(+id, updateUserDto);
    return {
      message: 'User updated successfully',
      data: user,
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    const user = await this.usersService.findone(+id);

    if (!user) {
      return {
        message: 'user not found',
        data: {},
      };
    }

    await this.usersService.remove(+id);

    return {
      message: 'User deleted successfully',
      data: user,
    };
  }
}
