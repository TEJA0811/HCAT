import { Module } from '@nestjs/common';
import { ManagersService } from './managers.service';
import { ManagersController } from './managers.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Manager } from './entities/manager.entity';
import { Team } from '../teams/entities/team.entity';
import { Project } from '../projects/entities/project.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Manager, Team, Project])],
  controllers: [ManagersController],
  providers: [ManagersService],
  exports: [ManagersService]
})
export class ManagersModule {}
