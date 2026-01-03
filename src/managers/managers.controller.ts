import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  ConflictException,
  Put,
} from '@nestjs/common';
import { ManagersService } from './managers.service';
import { CreateManagerDto } from './dto/create-manager.dto';
import { UpdateManagerDto } from './dto/update-manager.dto';

@Controller('managers')
export class ManagersController {
  constructor(private readonly managersService: ManagersService) {}

  @Post('create')
  async create(@Body() createManagerDto: CreateManagerDto) {
    const existingManager = await this.managersService.findBy({
      where: { email: createManagerDto.email },
    });

    if (existingManager) {
      throw new ConflictException('manager with this email already exists');
    }
    const manager = await this.managersService.create(createManagerDto);
    return {
      message: 'manager added',
      data: manager,
    };
  }

  @Get()
  async findAll() {
    const manager = await this.managersService.findAll();
    return {
      message: 'manager list',
      data: manager,
    };
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const manager = await this.managersService.findManagerWithRelations(+id);
    if (!manager) {
      return {
        message: 'manager not found',
        data: {},
      };
    }
    return {
      message: 'manager found',
      data: manager,
    };
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateManagerDto: UpdateManagerDto,
  ) {
    const existingManager = await this.managersService.findBy({
      where: { email: updateManagerDto.email },
    });

    if (existingManager) {
      throw new ConflictException('manager with this email already exists');
    }
    const manager = await this.managersService.findOne(+id);

    if (!manager) {
      return {
        message: 'manager not found',
        data: {},
      };
    }
    const updatedmanager = await this.managersService.update(
      +id,
      updateManagerDto,
    );
    return {
      message: 'manager updated successfully',
      data: updatedmanager,
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    const manager = await this.managersService.findOne(+id);

    if (!manager) {
      return {
        message: 'manager not found',
        data: {},
      };
    }

    await this.managersService.remove(+id);

    return {
      message: 'manager deleted successfully',
      data: manager,
    };
  }
}
